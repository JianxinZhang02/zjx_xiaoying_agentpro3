"""LangGraph owns the decision/execute/observe cycle and all task state."""
import copy
import json
import uuid
from datetime import datetime, timezone
from typing import Any, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.errors import GraphRecursionError
from langgraph.graph import END, START, StateGraph

from .model import ModelError
from .prompt import SYSTEM_PROMPT
from .schemas import TOOLS, validate_final
from .tools import ToolRuntime


class AgentState(TypedDict):
    messages: list[dict[str, Any]]
    pending_calls: list[dict[str, Any]]
    pending_results: list[dict[str, Any]]
    evidence: dict[str, dict[str, str]]
    failures: dict[str, Any]
    observations: list[dict[str, Any]]
    events: list[dict[str, Any]]
    model_calls: int
    tool_calls: int
    graph_steps: int
    stop_reason: str
    output: dict[str, Any]


def flatten_evidence(evidence):
    return {(doc, chunk): text for doc, chunks in evidence.items() for chunk, text in chunks.items()}


def nest_evidence(evidence):
    result = {}
    for (doc, chunk), text in evidence.items():
        result.setdefault(doc, {})[chunk] = text
    return result


class Agent:
    """A single task's compiled StateGraph; business decisions come from the model."""
    engine = "langgraph"

    def __init__(self, model, runtime, max_model_calls=8, max_tool_calls=10, graph_recursion_limit=None):
        if type(max_model_calls) is not int or type(max_tool_calls) is not int or min(max_model_calls, max_tool_calls) < 1:
            raise ValueError("Execution limits must be positive integers")
        if graph_recursion_limit is not None and (type(graph_recursion_limit) is not int or graph_recursion_limit < 1):
            raise ValueError("graph_recursion_limit must be a positive integer")
        self.model = model
        self.runtime = runtime
        self.max_model_calls = max_model_calls
        self.max_tool_calls = max_tool_calls
        self.recursion_limit = graph_recursion_limit or 6 * (max_model_calls + max_tool_calls) + 10
        self.thread_id = uuid.uuid4().hex
        self.events = []
        self.model_calls = 0
        self.tool_calls = 0
        self.state = None
        self.checkpointer = InMemorySaver()
        builder = StateGraph(AgentState)
        for name, node in (("decide", self._decide), ("execute_tools", self._execute_tools),
                           ("observe", self._observe), ("validate", self._validate),
                           ("finalize", self._finalize), ("stop", self._stop)):
            builder.add_node(name, node)
        builder.add_edge(START, "decide")
        builder.add_conditional_edges("decide", self._route_decision,
                                      {name: name for name in ("execute_tools", "validate", "decide", "stop")})
        builder.add_edge("execute_tools", "observe")
        builder.add_edge("validate", "observe")
        builder.add_conditional_edges("observe", self._route_observation,
                                      {name: name for name in ("decide", "finalize", "stop")})
        builder.add_edge("finalize", END)
        builder.add_edge("stop", END)
        self.graph = builder.compile(checkpointer=self.checkpointer)

    @staticmethod
    def _event(state, kind, **fields):
        state["events"].append({"event": kind, "index": len(state["events"]) + 1,
                                "timestamp": datetime.now(timezone.utc).isoformat(), **fields})

    def _enter(self, state, node):
        state = copy.deepcopy(state)
        state["graph_steps"] += 1
        self._event(state, "graph_node", node=node, graph_step=state["graph_steps"])
        return state

    def _decide(self, state):
        state = self._enter(state, "decide")
        state["pending_calls"] = []
        state["pending_results"] = []
        if state["model_calls"] >= self.max_model_calls:
            state["stop_reason"] = "model_call_limit"
            return state
        if state["tool_calls"] >= self.max_tool_calls:
            state["stop_reason"] = "tool_call_limit"
            return state
        state["model_calls"] += 1
        observed_ids = [m["tool_call_id"] for m in state["messages"] if m.get("role") == "tool"]
        self._event(state, "model_call", step=state["model_calls"], observed_tool_call_ids=observed_ids)
        try:
            response = self.model.complete(state["messages"], TOOLS)
        except ModelError as exc:
            self._event(state, "model_error", code=exc.code, message=str(exc))
            state["stop_reason"] = "model_error:" + exc.code
            return state
        if not isinstance(response, dict) or not isinstance(response.get("message"), dict):
            state["stop_reason"] = "invalid_model_response"
            return state
        message = response["message"]
        self._event(state, "model_response", step=state["model_calls"], message=message,
                    observed_tool_call_ids=observed_ids, usage=response.get("usage", {}),
                    request_id=response.get("request_id"), served_model=response.get("served_model"),
                    finish_reason=response.get("finish_reason"))
        calls = message.get("tool_calls") or []
        if not calls:
            state["messages"].append({"role": "assistant", "content": str(message.get("content") or "")})
            state["messages"].append({"role": "user", "content": "尚未结束。请选择工具，或调用 finish_answer 提交可校验的最终结果。"})
            return state
        if not isinstance(calls, list):
            state["stop_reason"] = "invalid_tool_call_envelope"
            return state
        ids = set()
        for call in calls:
            if (not isinstance(call, dict) or not isinstance(call.get("id"), str) or not call["id"]
                or call["id"] in ids or not isinstance(call.get("function"), dict)
                or not isinstance(call["function"].get("name"), str)):
                state["stop_reason"] = "invalid_tool_call_envelope"
                return state
            ids.add(call["id"])
        state["messages"].append(copy.deepcopy(message))
        state["pending_calls"] = copy.deepcopy(calls)
        return state

    @staticmethod
    def _route_decision(state):
        if state["stop_reason"]:
            return "stop"
        calls = state["pending_calls"]
        if not calls:
            return "decide"
        if len(calls) == 1 and calls[0]["function"]["name"] == "finish_answer":
            return "validate"
        return "execute_tools"

    def _tool_result(self, state, call, arguments, result):
        self._event(state, "tool_result", step=state["model_calls"], tool_call=state["tool_calls"],
                    call_id=call["id"], name=call["function"]["name"], arguments=arguments,
                    raw_arguments=call["function"].get("arguments") if arguments is None else None, result=result)
        state["pending_results"].append({"call_id": call["id"], "name": call["function"]["name"],
                                         "arguments": arguments, "result": result})

    @staticmethod
    def _parse(call):
        try:
            return json.loads(call["function"].get("arguments", "")), None
        except (ValueError, TypeError):
            return None, {"ok": False, "error": {"code": "invalid_json", "message": "Arguments must be a JSON object"}}

    def _execute_tools(self, state):
        state = self._enter(state, "execute_tools")
        runtime = ToolRuntime(self.runtime.kb, state["failures"])
        runtime.read_evidence = flatten_evidence(state["evidence"])
        for call in state["pending_calls"]:
            if state["tool_calls"] >= self.max_tool_calls:
                state["stop_reason"] = "tool_call_limit"
                break
            state["tool_calls"] += 1
            arguments, result = self._parse(call)
            if result is None:
                if call["function"]["name"] == "finish_answer":
                    result = {"ok": False, "error": {"code": "invalid_final", "messages": [
                        "finish_answer must be called alone after observing tool results"]}}
                else:
                    result = runtime.execute(call["function"]["name"], arguments)
            self._tool_result(state, call, arguments, result)
        state["evidence"] = nest_evidence(runtime.read_evidence)
        state["failures"] = copy.deepcopy(runtime.failures)
        state["observations"].extend(copy.deepcopy(runtime.observed))
        return state

    def _validate(self, state):
        state = self._enter(state, "validate")
        if state["tool_calls"] >= self.max_tool_calls:
            state["stop_reason"] = "tool_call_limit"
            return state
        state["tool_calls"] += 1
        call = state["pending_calls"][0]
        arguments, result = self._parse(call)
        if result is None:
            errors = validate_final(arguments, flatten_evidence(state["evidence"]))
            result = ({"ok": False, "error": {"code": "invalid_final", "messages": errors}}
                      if errors else {"ok": True, "accepted": True})
        self._tool_result(state, call, arguments, result)
        if result.get("accepted"):
            state["output"] = copy.deepcopy(arguments)
        return state

    def _observe(self, state):
        state = self._enter(state, "observe")
        delivered = []
        for observation in state["pending_results"]:
            state["messages"].append({"role": "tool", "tool_call_id": observation["call_id"],
                                      "content": json.dumps(observation["result"], ensure_ascii=False)})
            delivered.append(observation["call_id"])
        self._event(state, "observation_delivered", step=state["model_calls"], tool_call_ids=delivered)
        state["pending_calls"] = []
        state["pending_results"] = []
        if not state["output"] and not state["stop_reason"]:
            if state["tool_calls"] >= self.max_tool_calls:
                state["stop_reason"] = "tool_call_limit"
            elif state["model_calls"] >= self.max_model_calls:
                state["stop_reason"] = "model_call_limit"
        return state

    @staticmethod
    def _route_observation(state):
        if state["output"]:
            return "finalize"
        return "stop" if state["stop_reason"] else "decide"

    def _terminate(self, state, output, reason):
        output = copy.deepcopy(output)
        output["termination_reason"] = reason
        output["counts"] = {"model_calls": state["model_calls"], "tool_calls": state["tool_calls"]}
        state["output"] = output
        self._event(state, "termination", status=output["status"], reason=reason, counts=output["counts"])
        return state

    def _finalize(self, state):
        state = self._enter(state, "finalize")
        return self._terminate(state, state["output"], "model_finished")

    def _stop(self, state):
        state = self._enter(state, "stop")
        reason = state["stop_reason"] or "graph_stopped"
        output = {"status": "incomplete", "answer": "任务未完成：" + reason,
                  "citations": [{"doc_id": doc, "chunk_id": chunk, "quote": text}
                                for (doc, chunk), text in flatten_evidence(state["evidence"]).items()],
                  "conflicts": [], "gaps": [reason], "clarification_question": "", "reason": reason}
        return self._terminate(state, output, reason)

    def run(self, question, history=None):
        if self.state is not None:
            raise ValueError("Create a new Agent for each task; previous evidence cannot be reused implicitly")
        if not isinstance(question, str) or not question.strip():
            raise ValueError("question must be nonempty text")
        history = [] if history is None else history
        if not isinstance(history, list) or any(not isinstance(m, dict) or m.get("role") not in ("user", "assistant")
                                               or not isinstance(m.get("content"), str) for m in history):
            raise ValueError("history must contain user/assistant text messages only")
        initial: AgentState = {
            "messages": [{"role": "system", "content": SYSTEM_PROMPT}]
                        + [{"role": m["role"], "content": m["content"]} for m in history]
                        + [{"role": "user", "content": question}],
            "pending_calls": [], "pending_results": [], "evidence": nest_evidence(self.runtime.read_evidence),
            "failures": copy.deepcopy(self.runtime.failures), "observations": copy.deepcopy(self.runtime.observed),
            "events": [], "model_calls": 0, "tool_calls": 0, "graph_steps": 0, "stop_reason": "", "output": {},
        }
        self.graph_config = {"configurable": {"thread_id": self.thread_id}, "recursion_limit": self.recursion_limit}
        try:
            state = self.graph.invoke(initial, self.graph_config)
        except GraphRecursionError:
            state = copy.deepcopy(self.graph.get_state(self.graph_config).values or initial)
            state["stop_reason"] = "graph_recursion_limit"
            self._event(state, "graph_recursion_error", fallback="stop", reason="graph_recursion_limit")
            state = self._stop(state)
        self.state = copy.deepcopy(state)
        self.events = self.state["events"]
        self.model_calls, self.tool_calls = self.state["model_calls"], self.state["tool_calls"]
        self.runtime.read_evidence = flatten_evidence(self.state["evidence"])
        self.runtime.failures = copy.deepcopy(self.state["failures"])
        self.runtime.observed = copy.deepcopy(self.state["observations"])
        return copy.deepcopy(self.state["output"])

    def checkpoint_summary(self):
        return [{"step": snapshot.metadata.get("step"), "next": list(snapshot.next),
                 "model_calls": snapshot.values.get("model_calls", 0),
                 "tool_calls": snapshot.values.get("tool_calls", 0),
                 "checkpoint_id": snapshot.config.get("configurable", {}).get("checkpoint_id")}
                for snapshot in self.graph.get_state_history(self.graph_config)]

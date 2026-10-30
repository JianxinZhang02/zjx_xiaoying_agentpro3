"""Bounded model -> tool -> observation loop. No case-specific routing."""
import json
from datetime import datetime, timezone

from .model import ModelError
from .prompt import SYSTEM_PROMPT
from .schemas import TOOLS, validate_final


class Agent:
    def __init__(self, model, runtime, max_model_calls=8, max_tool_calls=10):
        if type(max_model_calls) is not int or type(max_tool_calls) is not int or min(max_model_calls, max_tool_calls) < 1:
            raise ValueError("Execution limits must be positive integers")
        self.model = model
        self.runtime = runtime
        self.max_model_calls = max_model_calls
        self.max_tool_calls = max_tool_calls
        self.events = []
        self.model_calls = 0
        self.tool_calls = 0

    def event(self, kind, **fields):
        self.events.append({"event": kind, "index": len(self.events) + 1,
                            "timestamp": datetime.now(timezone.utc).isoformat(), **fields})

    def finish(self, result, termination):
        result = dict(result)
        result["termination_reason"] = termination
        result["counts"] = {"model_calls": self.model_calls, "tool_calls": self.tool_calls}
        self.event("termination", status=result["status"], reason=termination, counts=result["counts"])
        return result

    def incomplete(self, reason):
        return self.finish({"status": "incomplete", "answer": "任务未完成：" + reason,
                            "citations": [{"doc_id": doc, "chunk_id": chunk, "quote": text}
                                          for (doc, chunk), text in self.runtime.read_evidence.items()],
                            "conflicts": [], "gaps": [reason], "clarification_question": "",
                            "reason": reason}, reason)

    def run(self, question, history=None):
        if not isinstance(question, str) or not question.strip():
            raise ValueError("question must be nonempty text")
        history = [] if history is None else history
        if not isinstance(history, list) or any(not isinstance(m, dict) or m.get("role") not in ("user", "assistant")
                                               or not isinstance(m.get("content"), str) for m in history):
            raise ValueError("history must contain user/assistant text messages only")
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend({"role": m["role"], "content": m["content"]} for m in history)
        messages.append({"role": "user", "content": question})
        while self.model_calls < self.max_model_calls:
            self.model_calls += 1
            self.event("model_call", step=self.model_calls)
            try:
                response = self.model.complete(messages, TOOLS)
            except ModelError as exc:
                self.event("model_error", code=exc.code, message=str(exc))
                return self.incomplete("model_error:" + exc.code)
            if not isinstance(response, dict) or not isinstance(response.get("message"), dict):
                return self.incomplete("invalid_model_response")
            message = response["message"]
            self.event("model_response", step=self.model_calls, message=message,
                       usage=response.get("usage", {}), request_id=response.get("request_id"),
                       served_model=response.get("served_model"), finish_reason=response.get("finish_reason"))
            calls = message.get("tool_calls") or []
            if not calls:
                messages.append({"role": "assistant", "content": str(message.get("content") or "")})
                messages.append({"role": "user", "content": "尚未结束。请选择工具，或调用 finish_answer 提交可校验的最终结果。"})
                continue
            if not isinstance(calls, list):
                return self.incomplete("invalid_tool_call_envelope")
            ids = set()
            for call in calls:
                if (not isinstance(call, dict) or not isinstance(call.get("id"), str) or not call["id"]
                    or call["id"] in ids or not isinstance(call.get("function"), dict)
                    or not isinstance(call["function"].get("name"), str)):
                    return self.incomplete("invalid_tool_call_envelope")
                ids.add(call["id"])
            messages.append(message)
            for call in calls:
                if self.tool_calls >= self.max_tool_calls:
                    return self.incomplete("tool_call_limit")
                self.tool_calls += 1
                name = call["function"]["name"]
                raw_args = call["function"].get("arguments", "")
                try:
                    args = json.loads(raw_args)
                except (ValueError, TypeError):
                    args = None
                    result = {"ok": False, "error": {"code": "invalid_json", "message": "Arguments must be a JSON object"}}
                else:
                    if name == "finish_answer":
                        errors = validate_final(args, self.runtime.read_evidence)
                        if len(calls) != 1:
                            errors.append("finish_answer must be called alone after observing tool results")
                        result = ({"ok": False, "error": {"code": "invalid_final", "messages": errors}}
                                  if errors else {"ok": True, "accepted": True})
                    else:
                        result = self.runtime.execute(name, args)
                self.event("tool_result", step=self.model_calls, tool_call=self.tool_calls,
                           call_id=call["id"], name=name, arguments=args,
                           raw_arguments=raw_args if args is None else None, result=result)
                messages.append({"role": "tool", "tool_call_id": call["id"],
                                 "content": json.dumps(result, ensure_ascii=False)})
                if name == "finish_answer" and result.get("accepted"):
                    return self.finish(args, "model_finished")
        return self.incomplete("model_call_limit")

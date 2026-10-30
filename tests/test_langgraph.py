import json
import tempfile
import unittest

from langgraph.graph.state import CompiledStateGraph

from knowledge_agent.agent import Agent
from knowledge_agent.evaluation import check_case
from knowledge_agent.mock import ScriptedModel, action, final
from knowledge_agent.retrieval import KnowledgeBase
from knowledge_agent.tools import ToolRuntime
from knowledge_agent.trace import decision_links, save_run


class LangGraphTests(unittest.TestCase):
    def setUp(self):
        self.kb = KnowledgeBase()
        self.read = action("read_document", doc_id="D04", purpose="核实原文")
        self.end = final(answer="年假至少提前 3 个工作日申请。", citations=[{
            "doc_id": "D04", "chunk_id": "C1", "quote": self.kb.read("D04", "C1")[1][0]["text"]}])

    def agent(self, steps=None, **kwargs):
        return Agent(ScriptedModel(steps or [self.read, self.end]), ToolRuntime(self.kb), **kwargs)

    def test_compiled_graph_and_state_own_task_data(self):
        agent = self.agent()
        self.assertIsInstance(agent.graph, CompiledStateGraph)
        result = agent.run("年假如何申请？")
        self.assertEqual(agent.state["output"], result)
        self.assertIn("D04", agent.state["evidence"])
        self.assertEqual(agent.state["tool_calls"], 2)
        self.assertTrue(any(snapshot["next"] for snapshot in agent.checkpoint_summary()))

    def test_observation_precedes_new_model_decision(self):
        agent = Agent(ScriptedModel([self.read, self.read, self.end]), ToolRuntime(self.kb, {"read_document": 1}))
        self.assertEqual(agent.run("年假？")["status"], "answered")
        failed = next(e for e in agent.events if e["event"] == "tool_result" and not e["result"]["ok"])
        link = next(link for link in decision_links(agent.events) if link["call_id"] == failed["call_id"])
        self.assertTrue(link["observation_delivered_to_next_model"])
        self.assertGreater(link["next_model_step"], failed["step"])
        self.assertEqual(link["next_actions"][0]["name"], "read_document")
        delivered = next(i for i, e in enumerate(agent.events) if e["event"] == "observation_delivered" and failed["call_id"] in e["tool_call_ids"])
        following = next(i for i, e in enumerate(agent.events) if e["event"] == "model_call" and failed["call_id"] in e["observed_tool_call_ids"])
        self.assertLess(delivered, following)

    def test_recursion_guard_is_an_explicit_incomplete(self):
        agent = self.agent(graph_recursion_limit=1)
        result = agent.run("年假？")
        self.assertEqual(result["status"], "incomplete")
        self.assertEqual(result["termination_reason"], "graph_recursion_limit")
        self.assertTrue(any(e["event"] == "graph_recursion_error" for e in agent.events))

    def test_graph_steps_and_model_budget_are_distinct(self):
        agent = self.agent(max_model_calls=2)
        self.assertEqual(agent.run("年假？")["status"], "answered")
        self.assertEqual(agent.model_calls, 2)
        self.assertGreater(agent.state["graph_steps"], 2)

    def test_new_task_cannot_reuse_old_evidence(self):
        agent = self.agent()
        agent.run("年假？")
        with self.assertRaises(ValueError):
            agent.run("另一个问题")

    def test_graph_trace_artifacts_are_actual_state(self):
        agent = self.agent()
        output = agent.run("年假？")
        with tempfile.TemporaryDirectory() as folder:
            saved = save_run(agent, {"question": "年假？"}, output, self.kb, folder)
            manifest = json.loads((saved / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["framework"]["version"], "1.2.18")
            self.assertEqual(manifest["engine"], "langgraph")
            self.assertEqual(json.loads((saved / "graph-state.json").read_text(encoding="utf-8")), agent.state)
            self.assertIn("execute_tools", (saved / "graph.mmd").read_text(encoding="utf-8"))
            self.assertTrue(json.loads((saved / "checkpoints.json").read_text(encoding="utf-8")))

    def test_same_batch_action_is_not_reported_as_feedback_decision(self):
        agent = self.agent([[self.read, action("read_document", doc_id="D03", purpose="补查")], self.end])
        agent.run("查询")
        links = decision_links(agent.events)
        self.assertEqual(links[0]["next_model_step"], 2)
        self.assertEqual([a["name"] for a in links[0]["next_actions"]], ["finish_answer"])

    def test_assessment_rejects_missing_observation_link(self):
        events = [{"event": "tool_result", "call_id": "fail", "step": 1, "name": "read_document", "arguments": {},
                   "result": {"ok": False, "error": {"code": "injected_failure"}}},
                  {"event": "model_response", "step": 2, "message": {"tool_calls": []}}]
        assessment = check_case({"expect": {"statuses": ["incomplete"], "observed_failure": True}},
                               {"status": "incomplete"}, events)
        self.assertIn("failure_not_linked_to_new_model_decision", assessment["failures"])


if __name__ == "__main__":
    unittest.main()

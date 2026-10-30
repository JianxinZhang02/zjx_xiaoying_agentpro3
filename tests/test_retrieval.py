import copy
import unittest

from knowledge_agent.retrieval import KnowledgeBase, tokenize
from knowledge_agent.tools import ToolRuntime


class RetrievalTests(unittest.TestCase):
    def test_chinese_bigrams_and_latin(self):
        self.assertEqual(tokenize("年假申请 IT"), ["年假", "假申", "申请", "it"])

    def test_normal_and_paraphrase_recall(self):
        kb = KnowledgeBase()
        for query in ("年假需要提前多久申请", "想休年假得提前几天跟主管说"):
            self.assertEqual(kb.search(query)[0]["doc_id"], "D04")

    def test_conflict_both_recalled(self):
        ids = {hit["doc_id"] for hit in KnowledgeBase().search("费用报销提交期限")}
        self.assertTrue({"D01", "D02"}.issubset(ids))

    def test_outside_and_deterministic_order(self):
        kb = KnowledgeBase()
        self.assertEqual(kb.search("火星地下海洋含盐量"), [])
        self.assertEqual(kb.search("报销"), kb.search("报销"))

    def test_read_unknown_and_chunk(self):
        kb = KnowledgeBase()
        with self.assertRaises(KeyError):
            kb.read("NOT_FOUND")
        self.assertEqual(len(kb.read("D04", "C1")[1]), 1)

    def test_changed_content_is_read_from_data(self):
        original = KnowledgeBase()
        data = copy.deepcopy(original.data)
        data["documents"][3]["chunks"][0]["text"] = "年假应至少提前 5 个工作日申请。"
        self.assertIn("5", KnowledgeBase(data=data).read("D04", "C1")[1][0]["text"])

    def test_failure_preserves_success_and_retry(self):
        tools = ToolRuntime(KnowledgeBase(), {"read_document": 1})
        args = {"doc_id": "D04", "purpose": "检查原文"}
        self.assertFalse(tools.execute("read_document", args)["ok"])
        self.assertEqual(tools.read_evidence, {})
        self.assertTrue(tools.execute("read_document", args)["ok"])
        tools.failures["read_document"] = "always"
        self.assertFalse(tools.execute("read_document", {"doc_id": "D03", "purpose": "补查"})["ok"])
        self.assertIn(("D04", "C1"), tools.read_evidence)

    def test_invalid_inputs_are_errors(self):
        tools = ToolRuntime(KnowledgeBase())
        for args in ({"query": "年假", "top_k": True, "purpose": "查阅"}, {"query": ""}, []):
            self.assertFalse(tools.execute("search_documents", args)["ok"])


if __name__ == "__main__":
    unittest.main()

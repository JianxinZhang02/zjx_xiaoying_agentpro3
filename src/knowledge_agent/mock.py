"""Explicitly SCRIPTED offline model. It is never evidence of LLM decisions."""
import copy
import json


def action(name, **arguments):
    return {"name": name, "arguments": arguments}


def final(status="answered", answer="", citations=None, conflicts=None, gaps=None, question="", reason="离线脚本结束"):
    return action("finish_answer", status=status, answer=answer, citations=citations or [],
                  conflicts=conflicts or [], gaps=gaps or [], clarification_question=question, reason=reason)


class ScriptedModel:
    mode = "mock"
    name = "SCRIPTED-OFFLINE-NOT-AN-LLM"

    def __init__(self, steps):
        self.steps = copy.deepcopy(steps)
        self.index = 0

    def complete(self, messages, tools):
        step = self.steps[min(self.index, len(self.steps) - 1)]
        self.index += 1
        if isinstance(step, Exception):
            raise step
        if "message" in step:
            return copy.deepcopy(step)
        actions = step if isinstance(step, list) else [step]
        calls = [{"id": "mock_{}_{}".format(self.index, i), "type": "function",
                  "function": {"name": item["name"], "arguments": json.dumps(item["arguments"], ensure_ascii=False)}}
                 for i, item in enumerate(actions)]
        return {"message": {"role": "assistant", "content": "", "tool_calls": calls},
                "usage": {}, "served_model": self.name}


def mock_for_case(case, kb):
    steps = [action("search_documents", query=case.get("query", case["question"]), purpose="离线脚本：检索")]
    citations = []
    failures = case.get("failures", {}).get("read_document", 0)
    for doc_id in case.get("read_docs", []):
        read = action("read_document", doc_id=doc_id, purpose="离线脚本：读取原文")
        steps.append(read)
        if failures == 1:
            steps.append(copy.deepcopy(read))
            failures = 0
        if failures != "always":
            _, chunks = kb.read(doc_id)
            citations.extend({"doc_id": doc_id, "chunk_id": c["chunk_id"], "quote": c["text"]}
                             for c in chunks if c["chunk_id"] != "C3")
    expected = case.get("expect", {})
    status = expected.get("statuses", ["insufficient_evidence"])[0]
    if expected.get("conflict"):
        steps.append(action("search_documents", query="报销制度适用范围优先关系替代", purpose="离线脚本：补查冲突关系"))
        steps.append(final(status, "两份原文分别规定 30 天和 15 天，适用范围和优先级不明。", citations,
                           ["D01 与 D02 的报销期限冲突"], ["缺少优先级和适用范围"], "请确认适用哪份报销制度？"))
    elif status == "insufficient_evidence":
        steps.append(action("search_documents", query="火星盐度", purpose="离线脚本：改写查询"))
        steps.append(final(status, "当前企业制度不包含该问题的可靠答案。", gaps=["缺少相关资料"]))
    elif status == "incomplete":
        steps.append(final(status, "原文读取工具持续失败，任务未完成。", citations, gaps=["未能成功读取原文"]))
    else:
        # Offline answer is a direct concatenation of the actual fixture text.
        answer = " ".join(c["quote"] for c in citations)
        steps.append(final("answered", answer, citations))
    return ScriptedModel(steps)

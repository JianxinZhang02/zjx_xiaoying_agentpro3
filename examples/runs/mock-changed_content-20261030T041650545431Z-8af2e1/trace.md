# 执行 Trace

模式：mock；模型：SCRIPTED-OFFLINE-NOT-AN-LLM；状态：answered

Mock 模式只验证流程，不证明真实模型决策。

## 步骤 1 / 工具调用 1：search_documents

动作说明：离线脚本：检索

参数：
```json
{
  "query": "年假申请",
  "purpose": "离线脚本：检索"
}
```

实际结果（完整，含返回摘要）：
```json
{
  "ok": true,
  "results": [
    {
      "doc_id": "D04",
      "title": "年假申请规则",
      "version_date": "2026-07-01",
      "scope": "全体正式员工",
      "score": 6.041902,
      "snippet": {
        "chunk_id": "C1",
        "text": "年假应至少提前 5 个工作日申请，经直属主管批准后生效。"
      }
    },
    {
      "doc_id": "D08",
      "title": "IT 服务申请",
      "version_date": "2026-06-01",
      "scope": "全体员工",
      "score": 1.031428,
      "snippet": {
        "chunk_id": "C1",
        "text": "办公设备故障应通过 IT 工单系统提交，描述设备编号和故障现象。"
      }
    },
    {
      "doc_id": "D02",
      "title": "费用报销管理办法 B",
      "version_date": "2026-09-01",
      "scope": "未注明",
      "score": 0.862608,
      "snippet": {
        "chunk_id": "C1",
        "text": "员工应在费用发生之日起 15 天内提交报销申请。"
      }
    },
    {
      "doc_id": "D01",
      "title": "费用报销管理办法 A",
      "version_date": "2026-08-01",
      "scope": "未注明",
      "score": 0.809603,
      "snippet": {
        "chunk_id": "C1",
        "text": "员工应在费用发生之日起 30 天内提交报销申请。"
      }
    }
  ]
}
```

后续动作：read_document

## 步骤 2 / 工具调用 2：read_document

动作说明：离线脚本：读取原文

参数：
```json
{
  "doc_id": "D04",
  "purpose": "离线脚本：读取原文"
}
```

实际结果（完整，含返回摘要）：
```json
{
  "ok": true,
  "document": {
    "doc_id": "D04",
    "title": "年假申请规则",
    "version_date": "2026-07-01",
    "scope": "全体正式员工"
  },
  "chunks": [
    {
      "chunk_id": "C1",
      "text": "年假应至少提前 5 个工作日申请，经直属主管批准后生效。"
    },
    {
      "chunk_id": "C2",
      "text": "年假天数依据个人任职情况核定，本文不提供每个人的可用余额。"
    }
  ],
  "untrusted_data": true
}
```

后续动作：finish_answer

## 步骤 3 / 工具调用 3：finish_answer

动作说明：离线脚本结束

参数：
```json
{
  "status": "answered",
  "answer": "年假应至少提前 5 个工作日申请，经直属主管批准后生效。 年假天数依据个人任职情况核定，本文不提供每个人的可用余额。",
  "citations": [
    {
      "doc_id": "D04",
      "chunk_id": "C1",
      "quote": "年假应至少提前 5 个工作日申请，经直属主管批准后生效。"
    },
    {
      "doc_id": "D04",
      "chunk_id": "C2",
      "quote": "年假天数依据个人任职情况核定，本文不提供每个人的可用余额。"
    }
  ],
  "conflicts": [],
  "gaps": [],
  "clarification_question": "",
  "reason": "离线脚本结束"
}
```

实际结果（完整，含返回摘要）：
```json
{
  "ok": true,
  "accepted": true
}
```

后续动作：model_finished

## 最终输出

```json
{
  "status": "answered",
  "answer": "年假应至少提前 5 个工作日申请，经直属主管批准后生效。 年假天数依据个人任职情况核定，本文不提供每个人的可用余额。",
  "citations": [
    {
      "doc_id": "D04",
      "chunk_id": "C1",
      "quote": "年假应至少提前 5 个工作日申请，经直属主管批准后生效。"
    },
    {
      "doc_id": "D04",
      "chunk_id": "C2",
      "quote": "年假天数依据个人任职情况核定，本文不提供每个人的可用余额。"
    }
  ],
  "conflicts": [],
  "gaps": [],
  "clarification_question": "",
  "reason": "离线脚本结束",
  "termination_reason": "model_finished",
  "counts": {
    "model_calls": 3,
    "tool_calls": 3
  }
}
```

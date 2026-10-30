# 执行 Trace

模式：mock；模型：SCRIPTED-OFFLINE-NOT-AN-LLM；状态：incomplete

Mock 模式只验证流程，不证明真实模型决策。

引擎：LangGraph 1.2.18

实际节点路径：decide → execute_tools → observe → decide → execute_tools → observe → decide → validate → observe → finalize

工具观察与后续模型动作的对应关系见 decision-links.json；状态与检查点见 graph-state.json / checkpoints.json。

## 步骤 1 / 工具调用 1：search_documents

动作说明：离线脚本：检索

参数：
```json
{
  "query": "年假申请",
  "purpose": "离线脚本：检索"
}
```

返回摘要：
```json
{
  "ok": true,
  "hits": 4,
  "doc_ids": [
    "D04",
    "D08",
    "D02",
    "D01"
  ]
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
        "text": "年假应至少提前 3 个工作日申请，经直属主管批准后生效。"
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

后续模型是否实际收到此观察：True

后续模型动作、参数及公开依据：
```json
[
  {
    "call_id": "mock_2_0",
    "name": "read_document",
    "arguments": {
      "doc_id": "D04",
      "purpose": "离线脚本：读取原文"
    },
    "public_basis": "离线脚本：读取原文"
  }
]
```

## 步骤 2 / 工具调用 2：read_document

动作说明：离线脚本：读取原文

参数：
```json
{
  "doc_id": "D04",
  "purpose": "离线脚本：读取原文"
}
```

返回摘要：
```json
{
  "ok": false,
  "error": {
    "code": "injected_failure",
    "message": "Synthetic tool failure. Retry or find other evidence; do not claim a successful read."
  }
}
```

实际结果（完整，含返回摘要）：
```json
{
  "ok": false,
  "error": {
    "code": "injected_failure",
    "message": "Synthetic tool failure. Retry or find other evidence; do not claim a successful read."
  }
}
```

后续动作：finish_answer

后续模型是否实际收到此观察：True

后续模型动作、参数及公开依据：
```json
[
  {
    "call_id": "mock_3_0",
    "name": "finish_answer",
    "arguments": {
      "status": "incomplete",
      "answer": "原文读取工具持续失败，任务未完成。",
      "citations": [],
      "conflicts": [],
      "gaps": [
        "未能成功读取原文"
      ],
      "clarification_question": "",
      "reason": "离线脚本结束"
    },
    "public_basis": "离线脚本结束"
  }
]
```

## 步骤 3 / 工具调用 3：finish_answer

动作说明：离线脚本结束

参数：
```json
{
  "status": "incomplete",
  "answer": "原文读取工具持续失败，任务未完成。",
  "citations": [],
  "conflicts": [],
  "gaps": [
    "未能成功读取原文"
  ],
  "clarification_question": "",
  "reason": "离线脚本结束"
}
```

返回摘要：
```json
{
  "ok": true,
  "accepted": true
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

后续模型是否实际收到此观察：False

后续模型动作、参数及公开依据：
```json
[]
```

## 最终输出

```json
{
  "status": "incomplete",
  "answer": "原文读取工具持续失败，任务未完成。",
  "citations": [],
  "conflicts": [],
  "gaps": [
    "未能成功读取原文"
  ],
  "clarification_question": "",
  "reason": "离线脚本结束",
  "termination_reason": "model_finished",
  "counts": {
    "model_calls": 3,
    "tool_calls": 3
  }
}
```

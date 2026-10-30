# 执行 Trace

模式：mock；模型：SCRIPTED-OFFLINE-NOT-AN-LLM；状态：answered

Mock 模式只验证流程，不证明真实模型决策。

引擎：LangGraph 1.2.18

实际节点路径：decide → execute_tools → observe → decide → execute_tools → observe → decide → validate → observe → finalize

工具观察与后续模型动作的对应关系见 decision-links.json；状态与检查点见 graph-state.json / checkpoints.json。

## 步骤 1 / 工具调用 1：search_documents

动作说明：离线脚本：检索

参数：
```json
{
  "query": "国内差旅报销材料",
  "purpose": "离线脚本：检索"
}
```

返回摘要：
```json
{
  "ok": true,
  "hits": 4,
  "doc_ids": [
    "D03",
    "D07",
    "D09",
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
      "doc_id": "D03",
      "title": "差旅报销材料清单",
      "version_date": "2026-08-15",
      "scope": "全体员工的国内差旅报销",
      "score": 11.800982,
      "snippet": {
        "chunk_id": "C1",
        "text": "国内差旅报销需要提供合规发票、行程单和出差审批单。"
      }
    },
    {
      "doc_id": "D07",
      "title": "国内差旅住宿标准",
      "version_date": "2026-08-10",
      "scope": "全体员工的国内差旅",
      "score": 7.618327,
      "snippet": {
        "chunk_id": "C1",
        "text": "国内差旅住宿报销上限为每晚 400 元；超出标准的部分需事前专项审批。"
      }
    },
    {
      "doc_id": "D09",
      "title": "新员工入职材料",
      "version_date": "2026-06-15",
      "scope": "新入职员工",
      "score": 1.624907,
      "snippet": {
        "chunk_id": "C1",
        "text": "新员工需向人力资源提交身份证明复印件、学历证明和银行卡信息。"
      }
    },
    {
      "doc_id": "D01",
      "title": "费用报销管理办法 A",
      "version_date": "2026-08-01",
      "scope": "未注明",
      "score": 1.408312,
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
      "doc_id": "D03",
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
  "doc_id": "D03",
  "purpose": "离线脚本：读取原文"
}
```

返回摘要：
```json
{
  "ok": true,
  "doc_id": "D03",
  "chunk_ids": [
    "C1",
    "C2"
  ]
}
```

实际结果（完整，含返回摘要）：
```json
{
  "ok": true,
  "document": {
    "doc_id": "D03",
    "title": "差旅报销材料清单",
    "version_date": "2026-08-15",
    "scope": "全体员工的国内差旅报销"
  },
  "chunks": [
    {
      "chunk_id": "C1",
      "text": "国内差旅报销需要提供合规发票、行程单和出差审批单。"
    },
    {
      "chunk_id": "C2",
      "text": "材料清单不规定报销提交期限；期限适用制度存在歧义时应向财务确认。"
    }
  ],
  "untrusted_data": true
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
      "status": "answered",
      "answer": "国内差旅报销需要提供合规发票、行程单和出差审批单。 材料清单不规定报销提交期限；期限适用制度存在歧义时应向财务确认。",
      "citations": [
        {
          "doc_id": "D03",
          "chunk_id": "C1",
          "quote": "国内差旅报销需要提供合规发票、行程单和出差审批单。"
        },
        {
          "doc_id": "D03",
          "chunk_id": "C2",
          "quote": "材料清单不规定报销提交期限；期限适用制度存在歧义时应向财务确认。"
        }
      ],
      "conflicts": [],
      "gaps": [],
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
  "status": "answered",
  "answer": "国内差旅报销需要提供合规发票、行程单和出差审批单。 材料清单不规定报销提交期限；期限适用制度存在歧义时应向财务确认。",
  "citations": [
    {
      "doc_id": "D03",
      "chunk_id": "C1",
      "quote": "国内差旅报销需要提供合规发票、行程单和出差审批单。"
    },
    {
      "doc_id": "D03",
      "chunk_id": "C2",
      "quote": "材料清单不规定报销提交期限；期限适用制度存在歧义时应向财务确认。"
    }
  ],
  "conflicts": [],
  "gaps": [],
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
  "status": "answered",
  "answer": "国内差旅报销需要提供合规发票、行程单和出差审批单。 材料清单不规定报销提交期限；期限适用制度存在歧义时应向财务确认。",
  "citations": [
    {
      "doc_id": "D03",
      "chunk_id": "C1",
      "quote": "国内差旅报销需要提供合规发票、行程单和出差审批单。"
    },
    {
      "doc_id": "D03",
      "chunk_id": "C2",
      "quote": "材料清单不规定报销提交期限；期限适用制度存在歧义时应向财务确认。"
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

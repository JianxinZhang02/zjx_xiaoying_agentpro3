# 执行 Trace

模式：mock；模型：SCRIPTED-OFFLINE-NOT-AN-LLM；状态：needs_clarification

Mock 模式只验证流程，不证明真实模型决策。

引擎：LangGraph 1.2.18

实际节点路径：decide → execute_tools → observe → decide → execute_tools → observe → decide → execute_tools → observe → decide → execute_tools → observe → decide → validate → observe → finalize

工具观察与后续模型动作的对应关系见 decision-links.json；状态与检查点见 graph-state.json / checkpoints.json。

## 步骤 1 / 工具调用 1：search_documents

动作说明：离线脚本：检索

参数：
```json
{
  "query": "费用报销提交期限",
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
    "D02",
    "D01",
    "D07"
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
      "score": 7.822933,
      "snippet": {
        "chunk_id": "C2",
        "text": "材料清单不规定报销提交期限；期限适用制度存在歧义时应向财务确认。"
      }
    },
    {
      "doc_id": "D02",
      "title": "费用报销管理办法 B",
      "version_date": "2026-09-01",
      "scope": "未注明",
      "score": 5.406786,
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
      "score": 5.348352,
      "snippet": {
        "chunk_id": "C1",
        "text": "员工应在费用发生之日起 30 天内提交报销申请。"
      }
    },
    {
      "doc_id": "D07",
      "title": "国内差旅住宿标准",
      "version_date": "2026-08-10",
      "scope": "全体员工的国内差旅",
      "score": 0.956546,
      "snippet": {
        "chunk_id": "C1",
        "text": "国内差旅住宿报销上限为每晚 400 元；超出标准的部分需事前专项审批。"
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
      "doc_id": "D01",
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
  "doc_id": "D01",
  "purpose": "离线脚本：读取原文"
}
```

返回摘要：
```json
{
  "ok": true,
  "doc_id": "D01",
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
    "doc_id": "D01",
    "title": "费用报销管理办法 A",
    "version_date": "2026-08-01",
    "scope": "未注明"
  },
  "chunks": [
    {
      "chunk_id": "C1",
      "text": "员工应在费用发生之日起 30 天内提交报销申请。"
    },
    {
      "chunk_id": "C2",
      "text": "本文未说明与其他报销制度的优先关系，也未注明适用部门。"
    }
  ],
  "untrusted_data": true
}
```

后续动作：read_document

后续模型是否实际收到此观察：True

后续模型动作、参数及公开依据：
```json
[
  {
    "call_id": "mock_3_0",
    "name": "read_document",
    "arguments": {
      "doc_id": "D02",
      "purpose": "离线脚本：读取原文"
    },
    "public_basis": "离线脚本：读取原文"
  }
]
```

## 步骤 3 / 工具调用 3：read_document

动作说明：离线脚本：读取原文

参数：
```json
{
  "doc_id": "D02",
  "purpose": "离线脚本：读取原文"
}
```

返回摘要：
```json
{
  "ok": true,
  "doc_id": "D02",
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
    "doc_id": "D02",
    "title": "费用报销管理办法 B",
    "version_date": "2026-09-01",
    "scope": "未注明"
  },
  "chunks": [
    {
      "chunk_id": "C1",
      "text": "员工应在费用发生之日起 15 天内提交报销申请。"
    },
    {
      "chunk_id": "C2",
      "text": "本文未说明替代哪份制度，也未注明适用部门。"
    }
  ],
  "untrusted_data": true
}
```

后续动作：search_documents

后续模型是否实际收到此观察：True

后续模型动作、参数及公开依据：
```json
[
  {
    "call_id": "mock_4_0",
    "name": "search_documents",
    "arguments": {
      "query": "报销制度适用范围优先关系替代",
      "purpose": "离线脚本：补查冲突关系"
    },
    "public_basis": "离线脚本：补查冲突关系"
  }
]
```

## 步骤 4 / 工具调用 4：search_documents

动作说明：离线脚本：补查冲突关系

参数：
```json
{
  "query": "报销制度适用范围优先关系替代",
  "purpose": "离线脚本：补查冲突关系"
}
```

返回摘要：
```json
{
  "ok": true,
  "hits": 4,
  "doc_ids": [
    "D01",
    "D02",
    "D03",
    "D06"
  ]
}
```

实际结果（完整，含返回摘要）：
```json
{
  "ok": true,
  "results": [
    {
      "doc_id": "D01",
      "title": "费用报销管理办法 A",
      "version_date": "2026-08-01",
      "scope": "未注明",
      "score": 10.246336,
      "snippet": {
        "chunk_id": "C2",
        "text": "本文未说明与其他报销制度的优先关系，也未注明适用部门。"
      }
    },
    {
      "doc_id": "D02",
      "title": "费用报销管理办法 B",
      "version_date": "2026-09-01",
      "scope": "未注明",
      "score": 4.399801,
      "snippet": {
        "chunk_id": "C2",
        "text": "本文未说明替代哪份制度，也未注明适用部门。"
      }
    },
    {
      "doc_id": "D03",
      "title": "差旅报销材料清单",
      "version_date": "2026-08-15",
      "scope": "全体员工的国内差旅报销",
      "score": 2.863,
      "snippet": {
        "chunk_id": "C2",
        "text": "材料清单不规定报销提交期限；期限适用制度存在歧义时应向财务确认。"
      }
    },
    {
      "doc_id": "D06",
      "title": "远程办公规则现行版",
      "version_date": "2026-10-01",
      "scope": "全体正式员工",
      "score": 2.763129,
      "snippet": {
        "chunk_id": "C1",
        "text": "本制度自 2026-10-01 起完整替代 D05《远程办公规则旧版》，适用于全体正式员工。"
      }
    }
  ]
}
```

后续动作：finish_answer

后续模型是否实际收到此观察：True

后续模型动作、参数及公开依据：
```json
[
  {
    "call_id": "mock_5_0",
    "name": "finish_answer",
    "arguments": {
      "status": "needs_clarification",
      "answer": "两份原文分别规定 30 天和 15 天，适用范围和优先级不明。",
      "citations": [
        {
          "doc_id": "D01",
          "chunk_id": "C1",
          "quote": "员工应在费用发生之日起 30 天内提交报销申请。"
        },
        {
          "doc_id": "D01",
          "chunk_id": "C2",
          "quote": "本文未说明与其他报销制度的优先关系，也未注明适用部门。"
        },
        {
          "doc_id": "D02",
          "chunk_id": "C1",
          "quote": "员工应在费用发生之日起 15 天内提交报销申请。"
        },
        {
          "doc_id": "D02",
          "chunk_id": "C2",
          "quote": "本文未说明替代哪份制度，也未注明适用部门。"
        }
      ],
      "conflicts": [
        "D01 与 D02 的报销期限冲突"
      ],
      "gaps": [
        "缺少优先级和适用范围"
      ],
      "clarification_question": "请确认适用哪份报销制度？",
      "reason": "离线脚本结束"
    },
    "public_basis": "离线脚本结束"
  }
]
```

## 步骤 5 / 工具调用 5：finish_answer

动作说明：离线脚本结束

参数：
```json
{
  "status": "needs_clarification",
  "answer": "两份原文分别规定 30 天和 15 天，适用范围和优先级不明。",
  "citations": [
    {
      "doc_id": "D01",
      "chunk_id": "C1",
      "quote": "员工应在费用发生之日起 30 天内提交报销申请。"
    },
    {
      "doc_id": "D01",
      "chunk_id": "C2",
      "quote": "本文未说明与其他报销制度的优先关系，也未注明适用部门。"
    },
    {
      "doc_id": "D02",
      "chunk_id": "C1",
      "quote": "员工应在费用发生之日起 15 天内提交报销申请。"
    },
    {
      "doc_id": "D02",
      "chunk_id": "C2",
      "quote": "本文未说明替代哪份制度，也未注明适用部门。"
    }
  ],
  "conflicts": [
    "D01 与 D02 的报销期限冲突"
  ],
  "gaps": [
    "缺少优先级和适用范围"
  ],
  "clarification_question": "请确认适用哪份报销制度？",
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
  "status": "needs_clarification",
  "answer": "两份原文分别规定 30 天和 15 天，适用范围和优先级不明。",
  "citations": [
    {
      "doc_id": "D01",
      "chunk_id": "C1",
      "quote": "员工应在费用发生之日起 30 天内提交报销申请。"
    },
    {
      "doc_id": "D01",
      "chunk_id": "C2",
      "quote": "本文未说明与其他报销制度的优先关系，也未注明适用部门。"
    },
    {
      "doc_id": "D02",
      "chunk_id": "C1",
      "quote": "员工应在费用发生之日起 15 天内提交报销申请。"
    },
    {
      "doc_id": "D02",
      "chunk_id": "C2",
      "quote": "本文未说明替代哪份制度，也未注明适用部门。"
    }
  ],
  "conflicts": [
    "D01 与 D02 的报销期限冲突"
  ],
  "gaps": [
    "缺少优先级和适用范围"
  ],
  "clarification_question": "请确认适用哪份报销制度？",
  "reason": "离线脚本结束",
  "termination_reason": "model_finished",
  "counts": {
    "model_calls": 5,
    "tool_calls": 5
  }
}
```

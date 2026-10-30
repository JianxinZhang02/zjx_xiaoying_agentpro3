# 执行 Trace

模式：mock；模型：SCRIPTED-OFFLINE-NOT-AN-LLM；状态：answered

Mock 模式只验证流程，不证明真实模型决策。

## 步骤 1 / 工具调用 1：search_documents

动作说明：离线脚本：检索

参数：
```json
{
  "query": "费用报销提交期限",
  "purpose": "离线脚本：检索"
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
      "score": 7.834659,
      "snippet": {
        "chunk_id": "C2",
        "text": "材料清单不规定报销提交期限；期限适用制度存在歧义时应向财务确认。"
      }
    },
    {
      "doc_id": "D01",
      "title": "费用报销管理办法 A",
      "version_date": "2026-08-01",
      "scope": "未注明",
      "score": 6.594823,
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
      "score": 1.119348,
      "snippet": {
        "chunk_id": "C1",
        "text": "国内差旅住宿报销上限为每晚 400 元；超出标准的部分需事前专项审批。"
      }
    },
    {
      "doc_id": "D08",
      "title": "IT 服务申请",
      "version_date": "2026-06-01",
      "scope": "全体员工",
      "score": 0.91842,
      "snippet": {
        "chunk_id": "C1",
        "text": "办公设备故障应通过 IT 工单系统提交，描述设备编号和故障现象。"
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
  "doc_id": "D01",
  "purpose": "离线脚本：读取原文"
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

后续动作：finish_answer

## 步骤 3 / 工具调用 3：finish_answer

动作说明：离线脚本结束

参数：
```json
{
  "status": "answered",
  "answer": "员工应在费用发生之日起 30 天内提交报销申请。 本文未说明与其他报销制度的优先关系，也未注明适用部门。",
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
  "answer": "员工应在费用发生之日起 30 天内提交报销申请。 本文未说明与其他报销制度的优先关系，也未注明适用部门。",
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

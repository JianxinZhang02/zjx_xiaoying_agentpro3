# 执行 Trace

模式：mock；模型：SCRIPTED-OFFLINE-NOT-AN-LLM；状态：insufficient_evidence

Mock 模式只验证流程，不证明真实模型决策。

## 步骤 1 / 工具调用 1：search_documents

动作说明：离线脚本：检索

参数：
```json
{
  "query": "火星地下海洋含盐量",
  "purpose": "离线脚本：检索"
}
```

实际结果（完整，含返回摘要）：
```json
{
  "ok": true,
  "results": []
}
```

后续动作：search_documents

## 步骤 2 / 工具调用 2：search_documents

动作说明：离线脚本：改写查询

参数：
```json
{
  "query": "火星盐度",
  "purpose": "离线脚本：改写查询"
}
```

实际结果（完整，含返回摘要）：
```json
{
  "ok": true,
  "results": []
}
```

后续动作：finish_answer

## 步骤 3 / 工具调用 3：finish_answer

动作说明：离线脚本结束

参数：
```json
{
  "status": "insufficient_evidence",
  "answer": "当前企业制度不包含该问题的可靠答案。",
  "citations": [],
  "conflicts": [],
  "gaps": [
    "缺少相关资料"
  ],
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
  "status": "insufficient_evidence",
  "answer": "当前企业制度不包含该问题的可靠答案。",
  "citations": [],
  "conflicts": [],
  "gaps": [
    "缺少相关资料"
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

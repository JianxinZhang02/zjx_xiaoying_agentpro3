# 项目提交说明 · LangGraph 版

- 题号：**3 · 企业知识问答 Agent**。
- GitHub：[JianxinZhang02/zjx_xiaoying_agentpro3](https://github.com/JianxinZhang02/zjx_xiaoying_agentpro3)。
- 当前架构：LangGraph 1.2.18，Python 3.10+（实测 3.12.13），项目 0.2.0。
- 模型：百炼 deepseek-v4.1-flash-1017。
- 最终 SHA：所有材料推送后，将 `git rev-parse HEAD` 完整结果填写投递页并核对远程；本文不自嵌自身提交哈希。

## 说明

本项目面向员工制度查询，采用 LangGraph StateGraph 编排模型决策、工具执行、观察回传、原文校验和终止。模型根据真实工具结果选择检索、读取、补查或结束；程序只负责运行边界，不以固定业务分支代替模型。图状态包含消息、成功证据、观察和调用计数，并保存真实节点路径、内存检查点摘要与编译图。

十篇合成制度带 ID、日期、适用范围和片段 ID，以 BM25 检索。引用必须来自本次成功读取的原文并逐字匹配；冲突无法消除时列出依据并请求确认，不凭日期擅自选制度。默认最多 8 次模型请求、10 次工具调用、单次超时 60 秒，上限明确 incomplete。

当前 44 个自动测试、14/14 Mock 和最终完整 14/14 live 场景通过，覆盖全部六项必验收。特别提供相同问题在单份/冲突资料，以及正常/读取故障下的对照。每次工具观察与后续实际模型动作、参数、公开依据通过 decision-links 关联，非预设决策日志，不公开内部思维。

旧原生版及首轮 LangGraph 12/14 的失败（超时、未问旁支内容）保留；修正通用输出约束后从干净源码全量重跑。Mock 是显式脚本，只证明执行机制。小样本通过不代表生产准确率，原文匹配不完全证明语义支持。

AI 辅助生成代码、资料、测试和文档，并执行实际验证；用户提供题目、仓库、范围、模型配置和 LangGraph 迁移要求。贡献如实记录，不冒称候选人独立实现或人工复核。InMemorySaver 仅用于运行内检查，未实现跨进程恢复、界面、部署、长期会话或生产隔离。

## 两个真实模型运行案例

以下案例均来自 LangGraph 版最终真实评估，使用百炼 `deepseek-v4.1-flash-1017`，不是离线 Mock。展示实际输出的关键字段；完整输出和逐步工具记录通过链接保留。

### 案例一：报销期限冲突，模型请求确认

**实际问题：**“员工费用发生后报销申请的提交期限是多久？”

**资料：**D01/C1 写明“员工应在费用发生之日起 30 天内提交报销申请。”；D02/C1 写明“员工应在费用发生之日起 15 天内提交报销申请。”。两份制度均未注明适用部门和相互优先/替代关系。

| 模型轮次 | 实际动作与参数 | 返回摘要 | 后续动作及公开依据 |
|---|---|---|---|
| 1 | 两次 `search_documents`：`query="费用报销申请 提交期限"`、`query="报销 费用发生 之日起 天内 提交"`，均 `top_k=10` | 找到 D01、D02 等相关制度 | 下一轮选择读取两份原文，核实时限和适用范围 |
| 2 | `read_document(doc_id="D01")`；`read_document(doc_id="D02")` | 分别规定 30 天与 15 天，均无适用部门和优先/替代关系 | 下一轮提交待确认结果；依据是冲突仍无法消除，不能擅自选一个期限 |
| 3 | `finish_answer(status="needs_clarification")` | 引用 D01/C1、D01/C2、D02/C1、D02/C2，提出澄清问题 | 本次任务结束，等待用户确认适用制度 |

**实际结果关键字段：**

```json
{
  "status": "needs_clarification",
  "clarification_question": "报销提交期限应适用《费用报销管理办法 A》（30 天）还是《费用报销管理办法 B》（15 天）？请确认适用部门或版本。",
  "gaps": [
    "两份报销办法均未注明适用范围与相互优先/替代关系，缺少判定依据。"
  ],
  "reason": "两份报销制度对同一事项给出不同期限，且均未注明适用范围或替代关系，冲突无法消除。",
  "counts": {"model_calls": 3, "tool_calls": 5}
}
```

该案例最终没有将 15 天或 30 天确定为唯一答案。工具结果引导模型从查证转向请求确认；版本日期没有被程序当作自动优先级。

证据：[实际输入](examples/runs/live-conflict-20261030T093409315561Z-b35108/input.json) · [完整实际输出](examples/runs/live-conflict-20261030T093409315561Z-b35108/output.json) · [逐步 Trace](examples/runs/live-conflict-20261030T093409315561Z-b35108/trace.md) · [观察与后续模型动作关联](examples/runs/live-conflict-20261030T093409315561Z-b35108/decision-links.json)。

### 案例二：读取失败后，模型观察错误并重新选择读取

**实际问题：**“国内差旅报销要准备哪些材料？”

**故障设置：**工具层注入第一次 `read_document` 失败。模型不接收预设答案或重试脚本，只能从实际工具返回中观察错误。

| 模型轮次 | 实际动作与参数 | 返回摘要 | 后续动作及公开依据 |
|---|---|---|---|
| 1 | 两次 `search_documents`：`query="国内差旅报销 材料"`、`query="差旅费报销 附件 凭证 要求"` | 找到 D03 及相关报销管理办法 | 下一轮选择读取原文核实材料要求 |
| 2 | 同轮选择读取 D03、D01、D02 | D03 返回 `injected_failure`；D01、D02 读取成功 | 实际结果经 observe 返回模型，成功结果保留 |
| 3 | 新一轮模型发起 `read_document(doc_id="D03", purpose="重试读取差旅报销材料清单原文")` | 读取成功：国内差旅报销需要提供合规发票、行程单和出差审批单 | 下一轮依据成功读取的 D03/C1 回答材料问题 |
| 4 | `finish_answer(status="answered")` | 回答三项材料，附原文引用，无未解决缺口 | 完成本轮任务 |

**实际结果关键字段：**

```json
{
  "status": "answered",
  "answer": "国内差旅报销需准备三项材料：合规发票、行程单和出差审批单。",
  "citations": [
    {
      "doc_id": "D03",
      "chunk_id": "C1",
      "quote": "国内差旅报销需要提供合规发票、行程单和出差审批单。"
    }
  ],
  "conflicts": [],
  "gaps": [],
  "counts": {"model_calls": 4, "tool_calls": 7}
}
```

第 3 轮重读来自观察错误后的新模型输出，不是程序自动重试。同轮预先选定的 D01/D02 读取不冒称为观察 D03 失败后的调整。

证据：[实际输入](examples/runs/live-transient_failure-20261030T093428549576Z-df6454/input.json) · [完整实际输出](examples/runs/live-transient_failure-20261030T093428549576Z-df6454/output.json) · [逐步 Trace](examples/runs/live-transient_failure-20261030T093428549576Z-df6454/trace.md) · [观察与后续模型动作关联](examples/runs/live-transient_failure-20261030T093428549576Z-df6454/decision-links.json)。

两个案例分别展示冲突后请求确认与故障后恢复，均包含实际工具结果到后续模型动作的闭环，不提交模型内部思维过程。

## 材料与复现

[README 安装命令](README.md) · [需求](docs/01-requirements.md) · [方案](docs/02-solution.md) · [实际评估](docs/03-evaluation.md) · [AI 使用](docs/04-ai-usage.md) · [复盘](docs/05-retrospective.md) · [完整讲解](docs/06-project-walkthrough.md) · [实际决策证据](examples/langgraph-react-proof.md) · [工作日志](docs/work-log.md)。

```powershell
uv sync --frozen --python 3.12
uv run --frozen python -m unittest discover -s tests -v
uv run --frozen python -m knowledge_agent evaluate --mode mock
# 按 README 配置百炼环境变量后
uv run --frozen python -m knowledge_agent run-case --case conflict --mode live
uv run --frozen python -m knowledge_agent run-case --case transient_failure --mode live
```

.env.example 仅是模板，不自动加载；密钥不随仓库提供。实际用时按阶段记录于 work-log，迁移与旧原生版分开计时。

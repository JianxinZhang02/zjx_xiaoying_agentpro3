# 项目提交补充说明 · LangGraph 版

- 题号：**3 · 企业知识问答 Agent**。
- GitHub：[JianxinZhang02/zjx_xiaoying_agentpro3](https://github.com/JianxinZhang02/zjx_xiaoying_agentpro3)。
- 当前架构：LangGraph 1.2.18，Python 3.10+（实测 3.12.13），项目 0.2.0。
- 模型：百炼 deepseek-v4.1-flash-1017。
- 最终 SHA：所有材料推送后，将 `git rev-parse HEAD` 完整结果填写投递页并核对远程；本文不自嵌自身提交哈希。

## 可粘贴的说明

本项目面向员工制度查询，采用 LangGraph StateGraph 编排模型决策、工具执行、观察回传、原文校验和终止。模型根据真实工具结果选择检索、读取、补查或结束；程序只负责运行边界，不以固定业务分支代替模型。图状态包含消息、成功证据、观察和调用计数，并保存真实节点路径、内存检查点摘要与编译图。

十篇合成制度带 ID、日期、适用范围和片段 ID，以 BM25 检索。引用必须来自本次成功读取的原文并逐字匹配；冲突无法消除时列出依据并请求确认，不凭日期擅自选制度。默认最多 8 次模型请求、10 次工具调用、单次超时 60 秒，上限明确 incomplete。

当前 44 个自动测试、14/14 Mock 和最终完整 14/14 live 场景通过，覆盖全部六项必验收。特别提供相同问题在单份/冲突资料，以及正常/读取故障下的对照。每次工具观察与后续实际模型动作、参数、公开依据通过 decision-links 关联，非预设决策日志，不公开内部思维。

旧原生版及首轮 LangGraph 12/14 的失败（超时、未问旁支内容）保留；修正通用输出约束后从干净源码全量重跑。Mock 是显式脚本，只证明执行机制。小样本通过不代表生产准确率，原文匹配不完全证明语义支持。

AI 辅助生成代码、资料、测试和文档，并执行实际验证；用户提供题目、仓库、范围、模型配置和 LangGraph 迁移要求。贡献如实记录，不冒称候选人独立实现或人工复核。InMemorySaver 仅用于运行内检查，未实现跨进程恢复、界面、部署、长期会话或生产隔离。

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

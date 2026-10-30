# 项目提交补充说明

## 提交字段

- 题号：**3 · 企业知识问答 Agent**。
- GitHub URL：[JianxinZhang02/zjx_xiaoying_agentpro3](https://github.com/JianxinZhang02/zjx_xiaoying_agentpro3)。
- 最终 commit SHA：在所有材料提交并推送后，将 `git rev-parse HEAD` 的完整结果填写到投递页独立字段；与远程 main 核对。本文不嵌入其自身提交哈希。
- 模型：阿里百炼工作空间中的 `deepseek-v4.1-flash-1017`。
- 运行方式：Python CLI。离线无需密钥，真实运行配置 DASHSCOPE 环境变量。

## 可粘贴到“说明、思路或补充内容”的文字

本项目选择题 3，面向员工制度查询，目标是在原文证据充分时回答，在资料缺失、制度冲突或工具失败时明确边界。实现采用 Python 标准库和原生模型工具调用循环，未依赖第三方 Agent 框架。模型自主选择检索、读取原文、补查或结束，程序负责执行、参数及引用校验、调用上限和 Trace。

提供 10 篇带文档 ID、版本日期、适用范围和片段 ID 的合成制度，通过中文双字词元 BM25 检索。最终引用必须来自本次成功读取的原文并逐字匹配；日期较新不自动代表制度优先。存在无法消除的冲突时，展示双方依据并请求确认，不擅自选择制度。

已提供 36 个自动测试及 12 组实际真实模型运行材料，覆盖六项必验收：明确答案、文档冲突、资料外问题、改写问题、上下文追问、工具失败，并补充持续故障、调用上限、资料修改、新旧替代和文档指令注入等验证。最终离线与真实矩阵均 12/12 通过；首轮真实 10/12 的失败、原因和通用提示词修正记录同样保留。持续故障正确返回未完成也属于该用例通过，不代表所有任务都成功回答。

运行记录包含实际输入、工具参数、结果、后续动作、简短公开依据、最终状态及数据/提示词/源码哈希。默认最多 8 次模型请求、10 次工具调用、单次请求超时 60 秒；达到上限明确返回 incomplete。已从独立 GitHub 克隆和干净虚拟环境完成无密钥复跑，提供可复制命令。

项目使用 AI 辅助生成代码、合成资料、测试和文档，并由 AI 借助工具执行实际验证及证据复核；候选人提供题目、选题、仓库、实现范围和模型配置。未虚报候选人独立手写或完成独立人工核验。离线 Mock 为显式脚本，只验证执行机制，不证明真实模型决策。小型合成语料和一次最终矩阵不能代表生产可靠率，引用匹配也不等于语义正确性的完全证明。

最初 MVP 核心实施与验证约 26 分钟，交付整理与本次讲解补充另记于实际工作日志。不含网页、线上部署、生产权限隔离、长期会话和大规模语义检索，这些不是本次 MVP 的交付范围。

## 评审材料入口

| 内容 | 入口 |
|---|---|
| 环境、安装、运行命令 | [README](README.md) |
| 用户、目标、范围、成功标准 | [01-requirements](docs/01-requirements.md) |
| 流程、动态决策与取舍 | [02-solution](docs/02-solution.md) |
| 预期、实际、失败、限制与每项输入/输出/Trace | [03-evaluation](docs/03-evaluation.md) |
| AI 范围、实际贡献与验证 | [04-ai-usage](docs/04-ai-usage.md) |
| 最难问题、收获与下一步 | [05-retrospective](docs/05-retrospective.md) |
| 完整讲解、案例与验收映射 | [06-project-walkthrough](docs/06-project-walkthrough.md) |
| 实际时间、修改与 Git 节点 | [work-log](docs/work-log.md) |
| 首轮失败与改进依据 | [first-live-review](examples/first-live-review.md) |
| 最终逐项证据复核 | [final-live-review](examples/final-live-review.md) |

## 最短复现命令

在仓库目录、Python 3.9+ 环境执行：

```powershell
python -m pip install -e .
python -m unittest discover -s tests -v
python -m knowledge_agent evaluate --mode mock
```

按 README 配好真实模型环境变量后：

```powershell
python -m knowledge_agent run-case --case normal --mode live
python -m knowledge_agent run-case --case conflict --mode live
python -m knowledge_agent run-case --case transient_failure --mode live
```

密钥不随仓库提供，.env.example 为模板且不会自动加载。.env 已被 Git 忽略。真实模型不可用时保留明确错误，不将 Mock 结果当真实验收。

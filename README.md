# 企业知识问答 Agent · 校招选题 3

面向员工的合成制度问答 CLI。模型自主选择检索、读取、补查或结束；程序负责工具执行、原文引用校验、调用上限及 Trace。

**评审入口：**[需求](docs/01-requirements.md) · [动态决策设计](docs/02-solution.md) · [实际评估与证据](docs/03-evaluation.md) · [AI 使用](docs/04-ai-usage.md) · [复盘](docs/05-retrospective.md)。

## 安装

要求 Python 3.9+、Git；开发环境为 Windows / Python 3.9.13。运行和测试均只用标准库，可编辑安装使用 setuptools 构建后端。

```powershell
git clone https://github.com/JianxinZhang02/zjx_xiaoying_agentpro3.git
cd zjx_xiaoying_agentpro3
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
```

以下命令中的 `python` 可替换为 `.\.venv\Scripts\python.exe`。macOS/Linux 对应解释器为 `.venv/bin/python`。
请在仓库目录运行；资料与验收输入位于仓库，不提供脱离仓库的独立 wheel 数据包。

## 无密钥离线运行

```powershell
python -m knowledge_agent run-case --case normal --mode mock
python -m knowledge_agent evaluate --mode mock
python -m unittest discover -s tests -v
```

Mock 是显式脚本化模型，标识为 `SCRIPTED-OFFLINE-NOT-AN-LLM`。它只验证执行机制，不证明真实模型决策效果。
任意 `ask --mode mock` 不生成自由问答，只演示资料不足路径；离线验收应使用 `run-case` / `evaluate`。

## 真实模型运行

使用阿里百炼兼容 Chat Completions 接口。`.env.example` 仅是模板，程序不会自动读取 `.env`；在当前 PowerShell 设置变量：

```powershell
$env:DASHSCOPE_API_KEY = "替换为本机密钥，不要提交"
$env:DASHSCOPE_BASE_URL = "https://ws-5u8f5tyzlwat3b13.cn-beijing.maas.aliyuncs.com/compatible-mode/v1"
$env:DASHSCOPE_MODEL = "deepseek-v4.1-flash-1017"

python scripts/check_model.py
python -m knowledge_agent ask --question "年假需要提前多久申请，由谁批准？" --mode live
python -m knowledge_agent run-case --case conflict --mode live
python -m knowledge_agent evaluate --mode live
```

使用自己的百炼空间时，同时替换地址与对应密钥。初始 `deepseek-v4-flash` 在本空间返回 404；经用户确认，最终使用 `deepseek-v4.1-flash-1017`。不会暗中切换模型或转为 Mock。

```powershell
python -m knowledge_agent evaluate --mode live --cases normal,conflict,context,transient_failure
python -m knowledge_agent run-case --case persistent_failure --mode live
python -m knowledge_agent ask --question "那需要哪些材料？" --history examples/cases/history.json --mode live
```

历史是 user/assistant 文本消息数组，只用于解析主题，不作为制度证据。
`--data` 替换 JSON 资料，`--out-dir` 指定运行目录；`ask` 还支持 `--max-model-calls`、`--max-tool-calls`。
默认上限为 8 次模型请求、10 次工具调用、单次请求超时 60 秒。重试与格式修正均计入额度，同轮多个工具逐个执行计数。

## 输出与证据

结果包含 `status`、`answer`、`citations`（文档/片段 ID、原文）、`conflicts`、`gaps`、`clarification_question`、`reason`、`termination_reason` 和调用计数。

| 状态 | 含义 |
|---|---|
| answered | 证据充分，已回答 |
| needs_clarification | 适用范围或冲突需要确认 |
| insufficient_evidence | 资料未覆盖问题 |
| incomplete | 工具、模型或执行上限导致未完成 |

`ask` 回答成功返回 0，其他任务状态返回 2；`run-case` / `evaluate` 按验收是否通过返回 0/1（持续故障正确返回 incomplete 也可通过该项）；无效输入返回 2。

每次运行保存 `input.json`、数据快照、结构化输出、Manifest、JSONL Trace 和由同一事件生成的 Markdown Trace。验收另有 `assessment.json`，汇总见 `examples/evaluations/`。
Manifest 记录源码提交及哈希、资料/提示词哈希、模式与模型。历史失败保留，最终评估文档明确链接交付使用的运行。

## 工程边界

- 10 篇合成制度，中文双字词元与英文词元 BM25；默认检索前 4 项，模型可以调整。
- 最终引用必须匹配本次成功读取的原文，搜索片段不能替代读取。
- 引用真实性与状态结构可自动校验，语义是否完全支持回答仍需复核；不虚报候选人已完成人工复核。
- 日期较新不自动优先，明确替代关系可以用于判断。资料外问题不接外部搜索。
- 有单项文档指令注入测试，不宣称生产级安全隔离。
- 无第三方 Agent 框架。项目版本 0.1.0；无第三方运行/测试依赖。

## Git 与提交

[实际开发记录](docs/work-log.md)记录时间、失败和修正；[首轮真实评估复核](examples/first-live-review.md)保留改进依据。
`.env`、虚拟环境、`.local/` 不提交。`python scripts/audit_secrets.py` 检查非忽略文件中的密钥形态字符串。

交付题号 **3**，GitHub URL 为本仓库。最终 SHA 在所有材料提交、推送后用 `git rev-parse HEAD` 获取，并与 `git ls-remote origin refs/heads/main` 核对。提交内部不嵌入其自身尚未生成的 SHA。

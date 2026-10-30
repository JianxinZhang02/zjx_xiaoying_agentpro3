# 企业知识问答 Agent · 选题 3 · LangGraph 版

当前版本 **0.2.0**：由 **LangGraph 1.2.18 StateGraph** 实际编排模型决策、工具执行、观察回传、引用校验和终止；模型使用百炼 `deepseek-v4.1-flash-1017`。

评审先看：[ReAct 真实决策证据](examples/langgraph-react-proof.md) · [全部验收与实际记录](docs/03-evaluation.md) · [完整讲解](docs/06-project-walkthrough.md) · [投递补充说明](SUBMISSION.md)。

## 环境与安装

要求 **Python 3.10+**，本次实测 **Python 3.12.13**。原版 Python 3.9 环境不能运行当前版。推荐用 uv 创建独立环境，避免修改系统 Python：

```powershell
git clone https://github.com/JianxinZhang02/zjx_xiaoying_agentpro3.git
cd zjx_xiaoying_agentpro3
uv python install 3.12
uv sync --frozen --python 3.12
```

`uv.lock` 锁定依赖；`pyproject.toml` 固定 LangGraph 1.2.18。无 uv 时，可在已安装的 Python 3.10+ 下新建 venv，再 `python -m pip install -e .`。
以下命令均在仓库目录执行。也可用 `.venv/Scripts/python.exe` 替代 `uv run --frozen python`。

## 离线运行与测试

```powershell
uv run --frozen python -m unittest discover -s tests -v
uv run --frozen python -m knowledge_agent run-case --case normal --mode mock
uv run --frozen python -m knowledge_agent evaluate --mode mock
```

Mock 为明确标记的 `SCRIPTED-OFFLINE-NOT-AN-LLM`，只验证图执行与保护机制，不证明模型决策效果。任意 `ask --mode mock` 仅演示资料不足路径，自由问答请用 live。

## 真实模型

`.env.example` 只是模板，不自动加载。在当前 PowerShell 配置：

```powershell
$env:DASHSCOPE_API_KEY = "替换为你的本机密钥"
$env:DASHSCOPE_BASE_URL = "https://ws-5u8f5tyzlwat3b13.cn-beijing.maas.aliyuncs.com/compatible-mode/v1"
$env:DASHSCOPE_MODEL = "deepseek-v4.1-flash-1017"
uv run --frozen python -m knowledge_agent ask --question "年假需要提前多久申请，由谁批准？" --mode live
uv run --frozen python -m knowledge_agent run-case --case conflict --mode live
uv run --frozen python -m knowledge_agent run-case --case transient_failure --mode live
uv run --frozen python -m knowledge_agent evaluate --mode live
```

使用自己的百炼空间时同时替换地址与对应密钥。不会自动换模型、降级成 Mock 或自动重试业务工具。
`--history examples/cases/history.json` 提供历史；`--data` 更换 JSON；`--out-dir` 指定证据目录；`evaluate --cases normal,conflict` 运行选定场景。
`ask` 支持 `--max-model-calls` 和 `--max-tool-calls`。

## 图与决策边界

```text
START → decide（真实模型选择动作）
          ├→ execute_tools → observe → decide
          ├→ validate → observe → finalize → END
          └→ stop → END
```

校验失败也经 observe 回到 decide。图状态保存消息、成功证据、失败配置、观察、计数和事件；不是在一个图节点中包住旧 while 循环。
条件边分发模型选定的动作、处理限额，不按问题关键词决定查哪篇制度。完整编译图见 [langgraph.mmd](docs/langgraph.mmd)。

默认最多 **8 次模型请求、10 次工具调用、单次模型超时 60 秒**。结束动作和错误修正均计数；框架递归保护也会返回明确 incomplete。
状态为 answered / needs_clarification / insufficient_evidence / incomplete。

## 输出、证据与复核

输出包含回答、原文引用、冲突、缺口、澄清问题、任务状态和终止原因。`ask` 成功回答退出 0，其他任务状态退出 2；验收命令按预期是否通过退出 0/1。
每个新运行保存输入、数据快照、实际输出、Manifest、JSONL/Markdown Trace，并增加：

- `decision-links.json`：每次工具观察 → 下一轮实际模型动作、参数和公开依据；同轮动作不冒充反馈决策。
- `graph-state.json`：实际最终图状态。
- `checkpoints.json`：运行期间真实内存检查点摘要。
- `graph.mmd`：实际编译图。

Manifest 标注 LangGraph 版本、Python、源码提交/哈希及依赖锁哈希。可用 `scripts/verify_react.py --summary <真实汇总路径>` 核对动作来源与观察关联。

## 当前验证与限制

当前图版本 **44 个自动测试、14/14 Mock、14/14 最终完整 live 场景通过**。首轮图版本为 12/14（一次超时、一次额外旁支内容），失败与修正均保留；以 [评估文档](docs/03-evaluation.md) 的链接为当前证据。
十篇制度均为合成数据；BM25 为词面检索。引用逐字匹配不等于语义正确性证明。语义复核由 AI 执行，未虚报候选人独立人工复核。
InMemorySaver 用于本次运行状态检查，不是跨进程持久化；未实现用户确认后恢复任务、生产部署或长期会话。

五份要求文档在 docs/01～05；AI 使用及实际贡献见 [04-ai-usage](docs/04-ai-usage.md)，实际用时和 Git 过程见 [work-log](docs/work-log.md)。历史 0.1 原生版记录保留，但不作为当前图版本的新验收结果。
`.env`、虚拟环境和 `.local/` 均忽略，`scripts/audit_secrets.py` 检查非忽略文件。提交题号 **3**；最终 SHA 在所有材料推送后获取并核对远程。

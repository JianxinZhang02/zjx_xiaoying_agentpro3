# LangGraph 方案、动态决策与取舍

当前 0.2.0 使用 LangGraph 1.2.18，实测 Python 3.12.13，要求 Python >=3.10。固定版本见 pyproject.toml，传递依赖见 uv.lock。

## 框架职责

`StateGraph(AgentState)` 定义六个节点，编译后由 graph.invoke 执行。START、END 与条件边负责运行编排；InMemorySaver 保存运行内检查点，方便核查实际状态。
不使用框架的自动重试策略，也不把原生 while 包进单个节点。工具失败必须先回传给模型，模型再发起新的动作。

| 节点 | 职责 |
|---|---|
| decide | 检查模型额度，调用真实模型，保存实际 tool_calls 与已观察的调用 ID |
| execute_tools | 执行模型选定的业务工具，计数，保留成功证据和错误 |
| observe | 将实际结果追加为 tool 消息，供下一轮模型观察 |
| validate | 验证模型提出的 finish_answer，错误也回传模型 |
| finalize | 结构校验通过后输出模型结果 |
| stop | 额度、模型异常或框架递归保护时明确 incomplete |

实际编译拓扑见 [langgraph.mmd](langgraph.mmd)，真实节点路径在每次 Trace 中。条件边只判断动作类型、校验结果和限额；是否补查、查什么、是否请求确认，由模型产生。

## 图状态

AgentState 包含 messages、pending_calls、pending_results、evidence、failures、observations、events、model_calls、tool_calls、graph_steps、stop_reason 和 output。
节点返回更新状态；业务工具从状态恢复本次已成功读取的证据，失败不会清空成果。Agent 实例只运行一次，防止新任务默默复用旧证据。
checkpoint 中没有模型密钥。InMemorySaver 不跨进程保存；graph-state.json 是审查快照，没有实现从它恢复任务。

## 模型与工具

模型为百炼 deepseek-v4.1-flash-1017，通过标准库 urllib 调用兼容 Chat Completions 接口；关闭思考模式，非流式，无传输层自动重试。
工具为 search_documents(query, top_k, purpose)、read_document(doc_id, chunk_id, purpose)、finish_answer（状态、回答、引用、冲突、缺口、澄清问题、公开结束依据）。
一轮可选择多个业务工具，程序串行执行，全部观察回传后才请求下一轮模型。同轮中第二个工具不能被说成观察第一个结果后的调整。
结束动作必须单独调用并经过 validate；仅输出“完成了”的普通文本不能结束。

## 检索与证据

十篇本地合成制度，中文双字词元/英文词元 BM25，默认 top_k=4，可由模型调至 1～10。标题和正文参与索引，日期/范围用于模型查证。
成功读取的原文登记在图状态。引用必须匹配本次读取的 doc_id/chunk_id 与原文子串。answered 需要引用且不得有未解决缺口；冲突至少引用两篇文档。
日期较新不代表优先；明确替代条款才可消解。程序不自动发现所有语义冲突，也不证明引用支持每句推理。

## 限额和 Trace

默认 8 次模型调用、10 次工具调用、网络超时 60 秒；结束动作、错误修正和模型决定的重试均计数。GraphRecursionError 也显式转换 incomplete，保留检查点中的成功证据。
JSONL 记录实际模型输出、工具执行及 observation_delivered；model_response 记录其实际收到的工具调用 ID。
decision-links 从这些实际事件生成下一动作、参数和公开 purpose/reason，不生成内部思维。图状态、内存检查点摘要和编译图一并输出。

## 原生版与新验收

原生版留在 Git 历史和旧 examples 中。用户要求迁移后，0.2 重新运行全部真实场景；不借用旧版结果冒充新框架验证。
框架作用是管理状态与执行，满足 ReAct 仍需看真实模型的动作和观察。核验入口见 [实际决策证据](../examples/langgraph-react-proof.md)。

官方参考：[Graph API](https://docs.langchain.com/oss/python/langgraph/graph-api)、[Persistence](https://docs.langchain.com/oss/python/langgraph/persistence)。

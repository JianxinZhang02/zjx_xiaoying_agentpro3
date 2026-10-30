# 项目讲解：LangGraph 版

当前提交为 0.2.0；旧原生版只作为历史。讲解时以当前真实 Trace 为准，不把框架名称当成决策效果证明。

## 一、业务目标与选题

员工需要可据以行动的制度答案，所以要给出处、核对适用范围，在冲突、缺资料或故障时说明边界。题 3 可用合成制度通过改数字、增删冲突文档、注入故障验证行为，范围适合 MVP。
结果不总是 answered：需要确认、资料不足和执行未完成都是有业务意义的结果。

## 二、当前架构

```text
CLI → 初始化 AgentState → LangGraph StateGraph.invoke
  decide → execute_tools → observe → decide
  decide → validate → observe → finalize → END
  额度/模型/递归异常 → stop → END（incomplete）
```

decide 内真实调用百炼模型；execute_tools 执行模型给出的名称和参数；observe 回传真实结果；validate 检查结束结果；finalize/stop 输出状态。
LangGraph 管理状态和节点执行。条件边根据模型的动作类型、结果校验和限额分发，不按用户问题写业务分支；工具错误不会直接路由成固定自动重试。

AgentState 保存 messages、pending_calls/results、evidence、failures、observations、events、model/tool 次数、图步数和 output。InMemorySaver 提供真实运行检查点；没有跨进程恢复功能。
入口导入 agent.py，实际图在 [graph_agent.py](../src/knowledge_agent/graph_agent.py)，不再由手写 while 调度。

## 三、模型怎样做决定

模型收到问题、可选历史、工具 Schema 和过去工具观察，返回 tool_calls。程序执行后把结果放入 role=tool 消息，并以 tool_call_id 对应动作；再次调用模型时带上这些结果。
模型负责查询词、读哪篇、是否补查/重读、请求确认或结束；程序负责白名单、参数、证据、计数和状态结构。
记录 purpose/reason 是简短公开依据，不保存内部思维过程。
同轮可能发出多个工具，当前串行执行；它们都是在本轮观察前选好的，不能把第二个冒称为基于第一个结果的调整。

## 四、检索与引用

十篇合成 JSON 制度附 doc_id、日期、scope、chunk_id。中文双字词元 BM25（如年假申请→年假/假申/申请），英文/数字按词；k1=1.5、b=0.75，默认 top_k=4，模型可选 1～10。
标题和正文用于索引，范围和日期用于核实；分数是词面相关性，不是事实概率或制度优先级。片段预先定义，没有自动文档解析和切块。
search 发现资料，read 核实原文并登记本次证据。最终 quote 必须逐字匹配本次成功读取的文档/片段，不能只引用搜索摘要。
程序仍不能保证每句推理被支持或检索已穷尽所有冲突。

## 五、状态与限制

answered：证据充分；needs_clarification：本轮问题的歧义/冲突；insufficient_evidence：资料没有覆盖；incomplete：工具/模型/额度导致未完成。
日期较新不自动优先，明确替代条款才有依据。只问材料时，无关期限冲突不阻断，也不应主动追加未问数字。
8 次模型调用、10 次工具调用、60 秒单次超时；结束、修正和模型决定的重读都计数。图递归保护也转成明确 incomplete，已有证据保留。

## 六、真实案例与原生版的区别

以 [ReAct 证据页](../examples/langgraph-react-proof.md) 的逐轮参数和结果为准：

- 同一报销期限问题：single_policy 只存在 D01，回答 30 天；conflict 加入 D02，读取双方后请求确认。动作和状态来自真实模型，程序未写“发现30/15就返回冲突”的业务判断。
- 同一材料问题：materials_normal 正常读取后结束；transient_failure 的 D03 首读失败，observe 回传后新的 decide 产生重读动作，成功后回答。
- 持续失败：模型尝试片段或补查后主动 incomplete；step_limit/tool_limit 则由程序额度终止，两类路径区分记录。
- 数据修改：年假 3 改 5 后，答案和引用随之变；D06 明确替代 D05 后使用现行 2 天。

迁移价值在于图状态、节点、观察回传与边界更加明确；满足考核的直接证据仍是实际模型输出和工具反馈，而不是架构名称。

## 七、技术、框架与源码阅读

| 技术 | 职责 |
|---|---|
| LangGraph 1.2.18 | StateGraph、条件边、START/END、InMemorySaver；实际运行编排 |
| Python 3.12.13（要求>=3.10） | 解释器，argparse/json/urllib/unittest 等 |
| 百炼 deepseek-v4.1-flash-1017 | 实际模型选择动作，标准库 HTTPS 接入 |
| BM25 | 小型制度的可解释词面检索 |
| uv.lock / pyproject.toml | 依赖锁定和安装，不再声称无运行依赖 |
| Git、JSONL、哈希 | 源码归因、真实事件与快照 |

LangChain 相关包是 LangGraph 的传递依赖，本项目没有使用 LangChain 的预构建 Agent。模型没有换成 Mock，仍使用原有真实接口。
源码阅读顺序：[cli](../src/knowledge_agent/cli.py) → [graph_agent](../src/knowledge_agent/graph_agent.py) → [tools](../src/knowledge_agent/tools.py)/[retrieval](../src/knowledge_agent/retrieval.py) → [schemas](../src/knowledge_agent/schemas.py) → [trace](../src/knowledge_agent/trace.py)/[evaluation](../src/knowledge_agent/evaluation.py)。

## 八、怎样证明与怎样演示

44 个自动测试验证执行机制，14/14 Mock 不证明模型决策；14/14 最终 live 记录真实行为，另有逐项 AI 语义复核。前次图版 12/14 的失败与修正保留。
每组保存实际 input/output/data/Trace、源码/提示词/依赖哈希，以及 decision-links、图状态、检查点与编译图。审计脚本核对工具参数来自模型且下一轮收到观察；不证明全部语义。
演示先看 single_policy/conflict 的同问题对照，再看 materials_normal/transient_failure，指出发生错误的调用 ID 与下一轮模型动作；最后看 step_limit/tool_limit 的明确未完成状态。

## 九、题目交付与个人贡献

五份要求文档、代码、测试、依赖、配置模板、GitHub 与完整 SHA 均提供。14 组真实输入/输出/Trace 覆盖六项必验收及边界，至少两条不同反馈路径见证据页。
AI 实现和复核、用户选题及模型配置、迁移要求如实记录；未虚报候选人独立手写或人工核验。原生版开发、补充讲解和本次迁移分别计时，不把中间空档算为开发。
提交材料见 [SUBMISSION](../SUBMISSION.md)，实际结果见 [evaluation](03-evaluation.md)，过程见 [work-log](work-log.md)。

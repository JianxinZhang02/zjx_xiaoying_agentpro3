# LangGraph 实际评估与限制

当前 0.2.0：LangGraph 1.2.18 / Python 3.12.13 / 百炼 deepseek-v4.1-flash-1017。**44 个测试、14/14 Mock、14/14 最终完整 live 通过**。
源码基线 `9c289aba6765f6c095b1b9a3b7f2f5734a214a73`，每次最终 Manifest 均 source_dirty=false。不是将原生版结果改名作为框架版记录。

- [自动测试输出](../examples/test-results-langgraph.txt)
- [最终 live 汇总](../examples/evaluations/live-20261030T093506576021Z.json)
- [最终 Mock 汇总](../examples/evaluations/mock-20261030T093540378160Z.json)
- [决策链审计结果](../examples/langgraph-react-audit.json)与[两组同问题对照](../examples/langgraph-react-proof.md)
- [当前逐项证据复核（AI 执行）](../examples/langgraph-live-review.md)
- [首轮图版 12/14 汇总](../examples/evaluations/live-20261030T093143170893Z.json)
- [超时用例单项复跑 1/1](../examples/evaluations/live-20261030T093154213642Z.json)

## 最终完整矩阵

| Case | Status | Model/tool calls | Input | Output | Trace | Decision links |
|---|---|---:|---|---|---|---|
| normal | answered | 3/4 | [input](../examples/runs/live-normal-20261030T093402356783Z-ff1ac1/input.json) | [output](../examples/runs/live-normal-20261030T093402356783Z-ff1ac1/output.json) | [Trace](../examples/runs/live-normal-20261030T093402356783Z-ff1ac1/trace.md) | [links](../examples/runs/live-normal-20261030T093402356783Z-ff1ac1/decision-links.json) |
| conflict | needs_clarification | 3/5 | [input](../examples/runs/live-conflict-20261030T093409315561Z-b35108/input.json) | [output](../examples/runs/live-conflict-20261030T093409315561Z-b35108/output.json) | [Trace](../examples/runs/live-conflict-20261030T093409315561Z-b35108/trace.md) | [links](../examples/runs/live-conflict-20261030T093409315561Z-b35108/decision-links.json) |
| outside | insufficient_evidence | 3/5 | [input](../examples/runs/live-outside-20261030T093413631133Z-6340cf/input.json) | [output](../examples/runs/live-outside-20261030T093413631133Z-6340cf/output.json) | [Trace](../examples/runs/live-outside-20261030T093413631133Z-6340cf/trace.md) | [links](../examples/runs/live-outside-20261030T093413631133Z-6340cf/decision-links.json) |
| paraphrase | answered | 3/4 | [input](../examples/runs/live-paraphrase-20261030T093417529711Z-d2e624/input.json) | [output](../examples/runs/live-paraphrase-20261030T093417529711Z-d2e624/output.json) | [Trace](../examples/runs/live-paraphrase-20261030T093417529711Z-d2e624/trace.md) | [links](../examples/runs/live-paraphrase-20261030T093417529711Z-d2e624/decision-links.json) |
| context | answered | 3/6 | [input](../examples/runs/live-context-20261030T093421754060Z-dd194e/input.json) | [output](../examples/runs/live-context-20261030T093421754060Z-dd194e/output.json) | [Trace](../examples/runs/live-context-20261030T093421754060Z-dd194e/trace.md) | [links](../examples/runs/live-context-20261030T093421754060Z-dd194e/decision-links.json) |
| transient_failure | answered | 4/7 | [input](../examples/runs/live-transient_failure-20261030T093428549576Z-df6454/input.json) | [output](../examples/runs/live-transient_failure-20261030T093428549576Z-df6454/output.json) | [Trace](../examples/runs/live-transient_failure-20261030T093428549576Z-df6454/trace.md) | [links](../examples/runs/live-transient_failure-20261030T093428549576Z-df6454/decision-links.json) |
| persistent_failure | incomplete | 6/6 | [input](../examples/runs/live-persistent_failure-20261030T093435216385Z-16b893/input.json) | [output](../examples/runs/live-persistent_failure-20261030T093435216385Z-16b893/output.json) | [Trace](../examples/runs/live-persistent_failure-20261030T093435216385Z-16b893/trace.md) | [links](../examples/runs/live-persistent_failure-20261030T093435216385Z-16b893/decision-links.json) |
| step_limit | incomplete | 1/2 | [input](../examples/runs/live-step_limit-20261030T093437364424Z-e500ad/input.json) | [output](../examples/runs/live-step_limit-20261030T093437364424Z-e500ad/output.json) | [Trace](../examples/runs/live-step_limit-20261030T093437364424Z-e500ad/trace.md) | [links](../examples/runs/live-step_limit-20261030T093437364424Z-e500ad/decision-links.json) |
| changed_content | answered | 3/5 | [input](../examples/runs/live-changed_content-20261030T093441804111Z-7f47a6/input.json) | [output](../examples/runs/live-changed_content-20261030T093441804111Z-7f47a6/output.json) | [Trace](../examples/runs/live-changed_content-20261030T093441804111Z-7f47a6/trace.md) | [links](../examples/runs/live-changed_content-20261030T093441804111Z-7f47a6/decision-links.json) |
| single_policy | answered | 5/9 | [input](../examples/runs/live-single_policy-20261030T093451105427Z-182a15/input.json) | [output](../examples/runs/live-single_policy-20261030T093451105427Z-182a15/output.json) | [Trace](../examples/runs/live-single_policy-20261030T093451105427Z-182a15/trace.md) | [links](../examples/runs/live-single_policy-20261030T093451105427Z-182a15/decision-links.json) |
| explicit_supersession | answered | 3/5 | [input](../examples/runs/live-explicit_supersession-20261030T093456077058Z-6c22f8/input.json) | [output](../examples/runs/live-explicit_supersession-20261030T093456077058Z-6c22f8/output.json) | [Trace](../examples/runs/live-explicit_supersession-20261030T093456077058Z-6c22f8/trace.md) | [links](../examples/runs/live-explicit_supersession-20261030T093456077058Z-6c22f8/decision-links.json) |
| document_injection | answered | 3/3 | [input](../examples/runs/live-document_injection-20261030T093459497024Z-dc18da/input.json) | [output](../examples/runs/live-document_injection-20261030T093459497024Z-dc18da/output.json) | [Trace](../examples/runs/live-document_injection-20261030T093459497024Z-dc18da/trace.md) | [links](../examples/runs/live-document_injection-20261030T093459497024Z-dc18da/decision-links.json) |
| materials_normal | answered | 3/6 | [input](../examples/runs/live-materials_normal-20261030T093504818582Z-4334d4/input.json) | [output](../examples/runs/live-materials_normal-20261030T093504818582Z-4334d4/output.json) | [Trace](../examples/runs/live-materials_normal-20261030T093504818582Z-4334d4/trace.md) | [links](../examples/runs/live-materials_normal-20261030T093504818582Z-4334d4/decision-links.json) |
| tool_limit | incomplete | 1/1 | [input](../examples/runs/live-tool_limit-20261030T093506451839Z-c67576/input.json) | [output](../examples/runs/live-tool_limit-20261030T093506451839Z-c67576/output.json) | [Trace](../examples/runs/live-tool_limit-20261030T093506451839Z-c67576/trace.md) | [links](../examples/runs/live-tool_limit-20261030T093506451839Z-c67576/decision-links.json) |

## 验证方法

状态、关键事实、引用、冲突/缺口、错误后的新模型动作、限额由自动规则检查。故障用例必须确认错误结果真的进入下一轮模型输入，并且有实际的新动作，不能只有固定日志。
每次工具执行需在同轮实际模型 tool_calls 中找到相同 ID、名称和参数；观察对应后续模型轮次必须严格大于原轮次。graph-state.events 与 JSONL 及最终输出一致。见 scripts/verify_react.py。
这证明运行记录的一致性与动作来源，不证明全部语义或穷尽所有制度。AI 助手逐项读取最终回答和证据复核，未冒称候选人独立人工复核。

## 失败与改进

首轮图版 12/14：normal 模型请求达到 60 秒超时，明确 incomplete，单项重跑通过；materials_normal 回答夹带未问 30/15 天数字，范围检查失败。保留失败，增强通用提示词及 finish_answer 的字段约束，未修改测试预期，之后完整重跑得到本次 14/14。
旧原生版曾有 10/12→12/12 迭代，旧材料仍保留，但不计为当前图版本验收。

## 限额与已知限制

step_limit 返回 incomplete/model_call_limit，tool_limit 返回 incomplete/tool_call_limit；框架递归保护由独立测试验证。持续工具故障由模型主动 incomplete，区别于被程序限额终止。
小型合成语料与一次最终完整矩阵不能估计生产可靠率。InMemorySaver 不跨进程恢复，没有用户确认后续跑、生产隔离或自动语义证明。

## 干净环境复跑

记录见 [LangGraph 独立克隆验证](../examples/clean-checkout-langgraph.txt)。该文件在独立克隆、Python 3.12 环境和 uv.lock 冻结安装后生成；旧 Python 3.9 克隆记录只属于历史原生版。

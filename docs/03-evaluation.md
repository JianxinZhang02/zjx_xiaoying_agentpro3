# 实际评估与限制

## 结果摘要

Windows / Python 3.9.13、百炼 deepseek-v4.1-flash-1017 上执行：**36 个自动测试通过，12/12 离线场景通过，12/12 真实模型场景通过**。
这是一次最终完整矩阵的样本结果，不是统计可靠率。持续失败与达到上限正确返回 incomplete，也属于相应故障场景通过。

- [自动测试原始输出](../examples/test-results.txt)
- [最终真实模型汇总](../examples/evaluations/live-20261030T042751763568Z.json)
- [最终 Mock 汇总](../examples/evaluations/mock-20261030T043037360312Z.json)
- [真实协议探针](../examples/connectivity/20261030T042311Z.json)
- [首轮真实汇总：10/12](../examples/evaluations/live-20261030T042505903362Z.json)及[失败复核](../examples/first-live-review.md)

最终矩阵使用提交 `7a86d58` 的实现；Manifest 保存完整源码提交与哈希，均 source_dirty=false。后续文档与证据提交不改变该源码版本。

## 六项验收与补充场景

| Case | Actual status | Model/tool calls | Input | Output | Trace |
|---|---|---:|---|---|---|
| normal | answered | 3/4 | [input](../examples/runs/live-normal-20261030T042650718907Z-86b32a/input.json) | [output](../examples/runs/live-normal-20261030T042650718907Z-86b32a/output.json) | [Trace](../examples/runs/live-normal-20261030T042650718907Z-86b32a/trace.md) |
| conflict | needs_clarification | 3/6 | [input](../examples/runs/live-conflict-20261030T042658023102Z-db244b/input.json) | [output](../examples/runs/live-conflict-20261030T042658023102Z-db244b/output.json) | [Trace](../examples/runs/live-conflict-20261030T042658023102Z-db244b/trace.md) |
| outside | insufficient_evidence | 2/3 | [input](../examples/runs/live-outside-20261030T042700874588Z-0dde60/input.json) | [output](../examples/runs/live-outside-20261030T042700874588Z-0dde60/output.json) | [Trace](../examples/runs/live-outside-20261030T042700874588Z-0dde60/trace.md) |
| paraphrase | answered | 3/4 | [input](../examples/runs/live-paraphrase-20261030T042705591623Z-ea9268/input.json) | [output](../examples/runs/live-paraphrase-20261030T042705591623Z-ea9268/output.json) | [Trace](../examples/runs/live-paraphrase-20261030T042705591623Z-ea9268/trace.md) |
| context | answered | 3/6 | [input](../examples/runs/live-context-20261030T042710617656Z-adcc59/input.json) | [output](../examples/runs/live-context-20261030T042710617656Z-adcc59/output.json) | [Trace](../examples/runs/live-context-20261030T042710617656Z-adcc59/trace.md) |
| transient_failure | answered | 4/7 | [input](../examples/runs/live-transient_failure-20261030T042717021187Z-d2c069/input.json) | [output](../examples/runs/live-transient_failure-20261030T042717021187Z-d2c069/output.json) | [Trace](../examples/runs/live-transient_failure-20261030T042717021187Z-d2c069/trace.md) |
| persistent_failure | incomplete | 6/7 | [input](../examples/runs/live-persistent_failure-20261030T042725623269Z-7eb039/input.json) | [output](../examples/runs/live-persistent_failure-20261030T042725623269Z-7eb039/output.json) | [Trace](../examples/runs/live-persistent_failure-20261030T042725623269Z-7eb039/trace.md) |
| step_limit | incomplete | 1/2 | [input](../examples/runs/live-step_limit-20261030T042727092916Z-3fda9c/input.json) | [output](../examples/runs/live-step_limit-20261030T042727092916Z-3fda9c/output.json) | [Trace](../examples/runs/live-step_limit-20261030T042727092916Z-3fda9c/trace.md) |
| changed_content | answered | 3/4 | [input](../examples/runs/live-changed_content-20261030T042731556796Z-289b21/input.json) | [output](../examples/runs/live-changed_content-20261030T042731556796Z-289b21/output.json) | [Trace](../examples/runs/live-changed_content-20261030T042731556796Z-289b21/trace.md) |
| single_policy | answered | 5/7 | [input](../examples/runs/live-single_policy-20261030T042741399630Z-c67248/input.json) | [output](../examples/runs/live-single_policy-20261030T042741399630Z-c67248/output.json) | [Trace](../examples/runs/live-single_policy-20261030T042741399630Z-c67248/trace.md) |
| explicit_supersession | answered | 3/5 | [input](../examples/runs/live-explicit_supersession-20261030T042747227466Z-8a46e5/input.json) | [output](../examples/runs/live-explicit_supersession-20261030T042747227466Z-8a46e5/output.json) | [Trace](../examples/runs/live-explicit_supersession-20261030T042747227466Z-8a46e5/trace.md) |
| document_injection | answered | 3/4 | [input](../examples/runs/live-document_injection-20261030T042751615455Z-dba930/input.json) | [output](../examples/runs/live-document_injection-20261030T042751615455Z-dba930/output.json) | [Trace](../examples/runs/live-document_injection-20261030T042751615455Z-dba930/trace.md) |

## 动态路径与改进证据

1. 明确答案：模型搜索后读取 D04，再结束并引用原文。
2. 冲突：模型搜索后读取 D01、D02 和辅助资料，观察到 30/15 天及缺失优先关系，改为请求确认。
3. 一次故障：D03 首次返回 injected_failure，同轮 D01/D02 成功结果保留；模型下一轮自行发起重读 D03，成功后回答。程序没有自动重试。
4. 持续故障：模型补查和读取均未取得原文，主动以 incomplete 结束；不将检索片段作为原文引用。
5. 资料扰动：normal 与 changed_content 从 3 变 5；single_policy 与 conflict 在加入 D02 后从 answered 变为 needs_clarification。

首轮自动检查 10/12：材料与故障恢复误受无关期限冲突影响，复核还发现无依据补充建议。保留首轮记录，修改通用提示词并增加回归约束后全量重跑，没有修改原预期状态来掩盖失败。

## 方法与边界

自动检查状态、关键事实、文档 ID、原文匹配、冲突与缺口、故障后模型动作及执行上限。词面规则不是通用语义裁判；实际输出的逐项复核见[最终证据复核](../examples/final-live-review.md)。
语义复核由 AI 助手执行，不冒称候选人完成独立人工复核。小型合成库、一次最终完整 live 矩阵不代表生产可靠率；引用校验不证明每句推理或穷尽所有制度。

最初工作空间 403、原模型名 404 的真实错误保留于 examples/connectivity。用户修正凭证并确认模型后成功，从未用 Mock 冒充真实链路。

## 干净环境复跑

已从 GitHub 独立克隆提交 `7a86d58cc9c8adc676ff4e78941057ba9bd0e822`，创建无系统 site-packages 的虚拟环境，按 README 安装。
从子进程环境移除模型密钥与 PYTHONPATH 后，36 个测试、12/12 Mock 场景及非回答退出码检查均通过。
原始命令、解释器路径、构建后端版本与输出见[干净环境记录](../examples/clean-checkout-verification.txt)。这是对最终代码版本的复跑，后续仅追加文档与证据。

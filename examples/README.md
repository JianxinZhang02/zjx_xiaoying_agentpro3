# 当前证据入口

- [LangGraph ReAct 实际路径与同问题对照](langgraph-react-proof.md)
- [当前全部验收与输入/输出/Trace](../docs/03-evaluation.md)
- [实际决策链审计](langgraph-react-audit.json)
- [LangGraph 测试输出](test-results-langgraph.txt)
- [当前独立克隆验证](clean-checkout-langgraph.txt)

每组新增 decision-links、graph-state、checkpoints 和编译图。manifest.engine=langgraph 标明图版本；无该字段的旧记录为原生版历史。
Mock 明确为脚本，不能证明模型决策。首轮图版失败和旧原生版失败均保留，不覆盖为最终成功。

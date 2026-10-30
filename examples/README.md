# 运行证据导航

- [最终矩阵及全部实际输入、输出、Trace](../docs/03-evaluation.md)
- [最终证据复核（AI 执行）](final-live-review.md)
- [首轮失败与修正依据](first-live-review.md)
- [自动测试原始输出](test-results.txt)

`runs/` 保留开发阶段和最终阶段记录，以评估文档链接为最终验收入口。`mock-*` 为显式离线脚本，`live-*` 为真实模型请求。
每个运行包含原始输入、实际输出、数据快照、JSONL/Markdown Trace 和来源哈希；失败不覆盖。

# 实际开发记录

时间使用 Asia/Shanghai。记录工具实际执行与验证，不补造候选人操作。

| 时间 | 工作 | 结果 / 提交 |
|---|---|---|
| 2026-10-30 12:08 | 检查环境、main 与 origin，开始实施 | Python 3.9.13；基线 98cfae8；工作区干净；保留 z.txt |
| 2026-10-30 12:09 | 使用现有 DASHSCOPE_API_KEY 对指定地址运行真实工具协议探针 | HTTP 403：Workspace endpoint access denied；证据 examples/connectivity/20261030T040928Z.json；未切换模型或伪装成功，继续独立实现 |
| 2026-10-30 12:10 | 使用用户提供的新密钥重试，密钥仅保存在被忽略的本机 .env | 工作空间 403 消失；deepseek-v4-flash 返回 HTTP 404 Model not exist；证据 examples/connectivity/20261030T041056Z.json；等待可用模型确认 |
| 2026-10-30 12:12 | 完成 10 篇合成制度、BM25、原文读取及故障注入 | 8 个离线测试通过；构建安装成功；首阶段提交 8af0e10 已推送 |
| 2026-10-30 12:16 | 完成原生 Agent 循环、结构化结束、引用校验、CLI、Trace 和 12 个离线用例 | 首轮离线矩阵 12/12 通过；均明确标记 SCRIPTED-OFFLINE-NOT-AN-LLM，不能证明真实决策 |
| 2026-10-30 12:19 | 完成边界测试并修正非对象参数的 Trace 保存、历史类型检查及 evaluate 自定义数据参数 | 36 个自动测试通过；数据工具提交 bf7a786 已推送；真实模型 ID 仍待确认 |
| 2026-10-30 12:23 | 用户确认模型 deepseek-v4.1-flash-1017，更新默认模型并运行真实协议探针 | 原地址原工作空间成功完成工具选择→本地执行→观察结果→回答；证据 examples/connectivity/20261030T042311Z.json；未使用 qwen-plus |
| 2026-10-30 12:25 | 完成首轮真实 12 场景评估并复核输出 | 自动 10/12；context、transient_failure 因无关期限冲突失败；另发现越界建议，见 examples/first-live-review.md；修正通用提示词并新增回归约束，36 个测试仍通过 |
| 2026-10-30 12:25 | 处理 GitHub schannel TLS 握手错误 | 使用单次命令 git -c http.sslBackend=openssl push 成功；未关闭 TLS 证书校验；模型接入提交 3e4969e 已推送 |

# 实际开发记录

时间使用 Asia/Shanghai。记录工具实际执行与验证，不补造候选人操作。

| 时间 | 工作 | 结果 / 提交 |
|---|---|---|
| 2026-10-30 12:08 | 检查环境、main 与 origin，开始实施 | Python 3.9.13；基线 98cfae8；工作区干净；保留 z.txt |
| 2026-10-30 12:09 | 使用现有 DASHSCOPE_API_KEY 对指定地址运行真实工具协议探针 | HTTP 403：Workspace endpoint access denied；证据 examples/connectivity/20261030T040928Z.json；未切换模型或伪装成功，继续独立实现 |
| 2026-10-30 12:10 | 使用用户提供的新密钥重试，密钥仅保存在被忽略的本机 .env | 工作空间 403 消失；deepseek-v4-flash 返回 HTTP 404 Model not exist；证据 examples/connectivity/20261030T041056Z.json；等待可用模型确认 |
| 2026-10-30 12:12 | 完成 10 篇合成制度、BM25、原文读取及故障注入 | 8 个离线测试通过；构建安装成功；首阶段提交 8af0e10 已推送 |

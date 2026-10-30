# 企业知识问答 Agent · 选题 3

Python 标准库实现的企业制度问答 CLI，提供真实模型工具循环、原文引用校验和可审查 Trace。

当前正在按 MVP 计划实施，实际结果以 `examples/` 和评估文档为准。

环境：Python 3.9+、Git。真实模型使用阿里百炼，需要 `DASHSCOPE_API_KEY`。
`.env.example` 仅是环境变量模板，不会自动加载。

```powershell
python -m pip install -e .
python scripts/check_model.py
```

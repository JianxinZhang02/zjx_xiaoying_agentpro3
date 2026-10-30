"""Explicit shell configuration; never implicitly load secrets from disk."""
import os
from dataclasses import dataclass, field


@dataclass
class ModelConfig:
    base_url: str = "https://ws-5u8f5tyzlwat3b13.cn-beijing.maas.aliyuncs.com/compatible-mode/v1"
    model: str = "deepseek-v4-flash"
    api_key: str = field(default="", repr=False)
    timeout: float = 60.0

    @classmethod
    def from_env(cls):
        return cls(
            base_url=os.environ.get("DASHSCOPE_BASE_URL", cls.base_url).rstrip("/"),
            model=os.environ.get("DASHSCOPE_MODEL", cls.model),
            api_key=os.environ.get("DASHSCOPE_API_KEY", ""),
        )


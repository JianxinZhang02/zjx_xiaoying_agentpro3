"""Small non-streaming Chat Completions transport; no automatic retries."""
import json
import socket
import urllib.error
import urllib.request


class ModelError(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


class LiveModel:
    mode = "live"

    def __init__(self, config):
        self.config = config
        self.name = config.model

    def complete(self, messages, tools):
        cfg = self.config
        if not cfg.api_key:
            raise ModelError("missing_api_key", "DASHSCOPE_API_KEY is not configured")
        if not cfg.base_url.startswith("https://"):
            raise ModelError("invalid_config", "Live endpoint must use HTTPS")
        payload = {
            "model": cfg.model, "messages": messages, "tools": tools,
            "stream": False, "enable_thinking": False,
            "temperature": 0.1, "max_tokens": 2048,
        }
        request = urllib.request.Request(
            cfg.base_url.rstrip("/") + "/chat/completions",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={"Authorization": "Bearer " + cfg.api_key,
                     "Content-Type": "application/json"}, method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=cfg.timeout) as response:
                data = json.load(response)
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace").replace(cfg.api_key, "[REDACTED]")[:600]
            raise ModelError("http_" + str(exc.code), detail) from None
        except (socket.timeout, TimeoutError):
            raise ModelError("timeout", "Model request timed out") from None
        except urllib.error.URLError as exc:
            raise ModelError("connection_error", str(exc.reason).replace(cfg.api_key, "[REDACTED]")) from None
        except (ValueError, OSError) as exc:
            raise ModelError("invalid_response", type(exc).__name__) from None
        try:
            raw = data["choices"][0]["message"]
            if not isinstance(raw, dict):
                raise ValueError("message is not an object")
            # No reasoning_content is persisted or returned to the application.
            message = {"role": "assistant", "content": raw.get("content") or ""}
            if raw.get("tool_calls"):
                message["tool_calls"] = raw["tool_calls"]
            return {"message": message, "usage": data.get("usage", {}),
                    "request_id": data.get("id"), "served_model": data.get("model", cfg.model),
                    "finish_reason": data["choices"][0].get("finish_reason")}
        except (KeyError, IndexError, TypeError, ValueError):
            raise ModelError("invalid_response", "Missing valid choices[0].message") from None

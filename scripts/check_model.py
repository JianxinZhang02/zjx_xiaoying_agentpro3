"""Paid live protocol probe. Save a redacted result, including failures."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from knowledge_agent.config import ModelConfig
from knowledge_agent.model import LiveModel, ModelError


def main():
    model = LiveModel(ModelConfig.from_env())
    tools = [{"type": "function", "function": {
        "name": "probe_document", "description": "Read the synthetic probe document.",
        "parameters": {"type": "object", "properties": {"doc_id": {"type": "string"}},
                       "required": ["doc_id"], "additionalProperties": False}}}]
    messages = [{"role": "user", "content": "Call probe_document with doc_id PROBE. After observing its result, reply with PROBE_OK followed by the returned value."}]
    result = {"timestamp": datetime.now(timezone.utc).isoformat(), "mode": "live",
              "requested_model": model.name, "passed": False}
    try:
        first = model.complete(messages, tools)
        result["first"] = first
        call = first["message"].get("tool_calls", [])[0]
        assert call["function"]["name"] == "probe_document"
        assert json.loads(call["function"]["arguments"]) == {"doc_id": "PROBE"}
        messages.append(first["message"])
        messages.append({"role": "tool", "tool_call_id": call["id"],
                         "content": json.dumps({"value": "synthetic-value-731"})})
        second = model.complete(messages, tools)
        result["second"] = second
        result["passed"] = "PROBE_OK" in second["message"]["content"] and "synthetic-value-731" in second["message"]["content"]
    except (ModelError, AssertionError, IndexError, KeyError, ValueError) as exc:
        result["error"] = {"code": getattr(exc, "code", type(exc).__name__), "message": str(exc)}
    target = Path("examples/connectivity")
    target.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = target / (stamp + ".json")
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": result["passed"], "evidence": str(path), "error": result.get("error")}, ensure_ascii=False))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())


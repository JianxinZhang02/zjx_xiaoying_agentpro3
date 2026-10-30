"""Persist one immutable run, with hashes and a human-readable event view."""
import hashlib
import json
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path

from .prompt import SYSTEM_PROMPT


ROOT = Path(__file__).resolve().parents[2]


def json_text(value):
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def write_text(path, text):
    with Path(path).open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def source_identity():
    def git(*args):
        try:
            return subprocess.check_output(["git", *args], cwd=str(ROOT), stderr=subprocess.DEVNULL).decode("utf-8").strip()
        except (OSError, subprocess.SubprocessError):
            return "unavailable"
    files = sorted((ROOT / "src" / "knowledge_agent").glob("*.py"))
    source_hash = hashlib.sha256()
    for path in files:
        source_hash.update(path.name.encode("utf-8"))
        source_hash.update(path.read_bytes())
    return {"git_commit": git("rev-parse", "HEAD"),
            "source_dirty": bool(git("status", "--porcelain", "--", "src", "data", "pyproject.toml")),
            "source_sha256": source_hash.hexdigest()}


def save_run(agent, run_input, output, kb, out_root=None, label="ask"):
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    run_id = "{}-{}-{}-{}".format(agent.model.mode, label, stamp, uuid.uuid4().hex[:6])
    folder = Path(out_root or ROOT / "examples" / "runs") / run_id
    folder.mkdir(parents=True, exist_ok=False)
    manifest = {"run_id": run_id, "timestamp": datetime.now(timezone.utc).isoformat(),
                "display_timezone": "Asia/Shanghai", "mode": agent.model.mode, "requested_model": agent.model.name,
                "limits": {"model_calls": agent.max_model_calls, "tool_calls": agent.max_tool_calls},
                "data_sha256": digest(kb.data), "prompt_sha256": digest(SYSTEM_PROMPT), **source_identity(),
                "mock_boundary": "Scripted model validates execution only, not real model decisions" if agent.model.mode == "mock" else None}
    write_text(folder / "manifest.json", json_text(manifest))
    write_text(folder / "input.json", json_text(run_input))
    write_text(folder / "data.json", json_text(kb.data))
    write_text(folder / "output.json", json_text(output))
    write_text(folder / "trace.jsonl", "".join(json.dumps(e, ensure_ascii=False) + "\n" for e in agent.events))
    lines = ["# 执行 Trace", "", "模式：{}；模型：{}；状态：{}".format(agent.model.mode, agent.model.name, output["status"]),
             "", "Mock 模式只验证流程，不证明真实模型决策。" if agent.model.mode == "mock" else "本记录来自真实模型调用。", ""]
    for index, event in enumerate(agent.events):
        if event["event"] == "tool_result":
            arguments = event.get("arguments")
            args = arguments if isinstance(arguments, dict) else {}
            next_event = next((e for e in agent.events[index + 1:] if e["event"] in ("model_response", "termination", "model_error")), None)
            if next_event and next_event["event"] == "model_response":
                next_action = ", ".join(c["function"]["name"] for c in next_event["message"].get("tool_calls", [])) or "模型输出文本，需继续规范化"
            else:
                next_action = next_event.get("reason", next_event.get("code", "结束")) if next_event else "无后续事件"
            lines.extend(["## 步骤 {} / 工具调用 {}：{}".format(event["step"], event["tool_call"], event["name"]), "",
                          "动作说明：" + str(args.get("purpose", args.get("reason", "参数格式错误"))), "",
                          "参数：", "```json", json_text(arguments).rstrip(), "```", "",
                          "实际结果（完整，含返回摘要）：", "```json", json_text(event["result"]).rstrip(), "```", "",
                          "后续动作：" + next_action, ""])
        elif event["event"] == "model_error":
            lines.extend(["模型错误：" + event["code"], "", event["message"], ""])
    lines.extend(["## 最终输出", "", "```json", json_text(output).rstrip(), "```", ""])
    write_text(folder / "trace.md", "\n".join(lines))
    return folder

"""Audit real LangGraph runs against actual model calls, tool receipts and state."""
import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def verify_summary(path):
    summary = json.loads(Path(path).read_text(encoding="utf-8"))
    require(summary.get("mode") == "live" and summary.get("engine") == "langgraph", "Real LangGraph summary required")
    runs = {}
    for row in summary["results"]:
        folder = Path(row["run_dir"])
        if not folder.is_absolute():
            folder = ROOT / folder
        load = lambda name: json.loads((folder / name).read_text(encoding="utf-8"))
        manifest, state, output = load("manifest.json"), load("graph-state.json"), load("output.json")
        events = [json.loads(line) for line in (folder / "trace.jsonl").read_text(encoding="utf-8").splitlines()]
        require(manifest["engine"] == "langgraph" and manifest["mode"] == "live", row["case"] + ": wrong engine/mode")
        require(not manifest["source_dirty"], row["case"] + ": source was dirty")
        require(events == state["events"] and output == state["output"], row["case"] + ": artifacts disagree")
        responses = {e["step"]: e for e in events if e["event"] == "model_response"}
        for event in events:
            if event["event"] != "tool_result":
                continue
            response = responses[event["step"]]
            call = next((c for c in response["message"].get("tool_calls", []) if c["id"] == event["call_id"]), None)
            require(call is not None and call["function"]["name"] == event["name"], "Tool action missing from actual model output")
            try:
                args = json.loads(call["function"]["arguments"])
            except (ValueError, TypeError):
                args = None
            require(args == event["arguments"], "Tool parameters differ from actual model output")
        for link in load("decision-links.json"):
            if link["next_model_step"] is not None:
                response = responses[link["next_model_step"]]
                require(link["observation_delivered_to_next_model"] and link["call_id"] in response["observed_tool_call_ids"],
                        "Observation not delivered before the claimed next decision")
                require(link["next_model_step"] > link["step"], "Same-round actions cannot be feedback decisions")
        require(output["counts"]["model_calls"] <= manifest["limits"]["model_calls"], "Model limit exceeded")
        require(output["counts"]["tool_calls"] <= manifest["limits"]["tool_calls"], "Tool limit exceeded")
        require(any(e["event"] == "graph_node" and e["node"] == "decide" for e in events), "Graph did not execute decide")
        runs[row["case"]] = {"input": load("input.json"), "output": output, "links": load("decision-links.json")}
    if {"single_policy", "conflict"}.issubset(runs):
        a, b = runs["single_policy"], runs["conflict"]
        require(a["input"]["question"] == b["input"]["question"], "Conflict comparison needs identical questions")
        require(a["output"]["status"] == "answered" and b["output"]["status"] == "needs_clarification", "Conflict evidence did not change outcome")
    if {"materials_normal", "transient_failure"}.issubset(runs):
        a, b = runs["materials_normal"], runs["transient_failure"]
        require(a["input"]["question"] == b["input"]["question"], "Failure comparison needs identical questions")
        require(any(not link["result_summary"]["ok"] and link["observation_delivered_to_next_model"] and link["next_actions"]
                    for link in b["links"]), "No model action after actual failure")
    return {"verified_runs": len(runs), "engine": "langgraph", "mode": "live", "passed": True,
            "boundary": "Artifact/protocol consistency audit, not proof of every semantic judgment."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", required=True)
    print(json.dumps(verify_summary(parser.parse_args().summary), ensure_ascii=False))

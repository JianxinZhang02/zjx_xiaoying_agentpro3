"""CLI entry points. Non-answer results and failed evaluations have nonzero exit codes."""
import argparse
import json
import sys
from pathlib import Path

from .agent import Agent
from .config import ModelConfig
from .evaluation import evaluate, load_cases, run_case
from .mock import mock_for_case
from .model import LiveModel
from .retrieval import DEFAULT_DATA, KnowledgeBase
from .tools import ToolRuntime
from .trace import save_run


def main(argv=None):
    # Keep Chinese output portable in Windows terminals and redirected logs.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="企业制度知识问答 Agent（合成资料）")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("ask", "run-case", "evaluate"):
        item = sub.add_parser(name)
        item.add_argument("--mode", choices=("live", "mock"), default="mock")
        item.add_argument("--out-dir", type=Path)
        item.add_argument("--data", type=Path, default=DEFAULT_DATA)
        if name == "ask":
            item.add_argument("--question", required=True)
            item.add_argument("--history", type=Path)
            item.add_argument("--max-model-calls", type=int, default=8)
            item.add_argument("--max-tool-calls", type=int, default=10)
        elif name == "run-case":
            item.add_argument("--case", required=True)
        else:
            item.add_argument("--cases", help="Comma-separated case IDs; omit to run all")
    args = parser.parse_args(argv)
    try:
        if args.command == "evaluate":
            summary, path = evaluate(args.mode, args.cases.split(",") if args.cases else None, args.out_dir, args.data)
            print(json.dumps({"summary": str(path), "passed": summary["passed"], "total": summary["total"]}, ensure_ascii=False))
            return 0 if not summary["failed"] else 1
        if args.command == "run-case":
            case = next((case for case in load_cases() if case["id"] == args.case), None)
            if case is None:
                raise ValueError("Unknown case: " + args.case)
            row = run_case(case, args.mode, args.out_dir, args.data)
            print(json.dumps(row, ensure_ascii=False, indent=2))
            return 0 if row["passed"] else 1
        kb = KnowledgeBase(args.data)
        history = json.loads(args.history.read_text(encoding="utf-8")) if args.history else []
        if args.mode == "mock":
            # Arbitrary mock questions deliberately cannot claim a generated answer.
            case = {"question": args.question, "query": args.question, "read_docs": [],
                    "expect": {"statuses": ["insufficient_evidence"]}}
            model = mock_for_case(case, kb)
        else:
            model = LiveModel(ModelConfig.from_env())
        agent = Agent(model, ToolRuntime(kb), args.max_model_calls, args.max_tool_calls)
        output = agent.run(args.question, history)
        folder = save_run(agent, {"question": args.question, "history": history}, output, kb, args.out_dir)
        print(json.dumps({"mode": args.mode, "output": output, "run_dir": str(folder)}, ensure_ascii=False, indent=2))
        return 0 if output["status"] == "answered" else 2
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(json.dumps({"status": "incomplete", "error": type(exc).__name__, "message": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())

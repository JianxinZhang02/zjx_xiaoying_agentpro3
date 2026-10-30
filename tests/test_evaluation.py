import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from knowledge_agent.cli import main
from knowledge_agent.evaluation import evaluate, load_cases, run_case


class EvaluationTests(unittest.TestCase):
    def test_all_offline_cases_without_network(self):
        with tempfile.TemporaryDirectory() as folder, patch("urllib.request.urlopen", side_effect=AssertionError("Network forbidden")):
            for case in load_cases():
                with self.subTest(case=case["id"]):
                    result = run_case(case, "mock", Path(folder))
                    self.assertTrue(result["passed"], result)

    def test_live_missing_key_is_saved_and_fails_assessment(self):
        with tempfile.TemporaryDirectory() as folder, patch.dict("os.environ", {"DASHSCOPE_API_KEY": ""}):
            result = run_case(load_cases()[0], "live", Path(folder))
            self.assertFalse(result["passed"])
            output = json.loads((Path(result["run_dir"]) / "output.json").read_text(encoding="utf-8"))
            self.assertEqual(output["termination_reason"], "model_error:missing_api_key")

    def test_cli_exit_status_and_unknown_case(self):
        with tempfile.TemporaryDirectory() as folder, contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(["run-case", "--case", "normal", "--out-dir", folder]), 0)
            self.assertEqual(main(["run-case", "--case", "unknown"]), 2)
            self.assertEqual(main(["ask", "--question", "anything", "--out-dir", folder]), 2)

    def test_evaluate_cli_passes_custom_data(self):
        with patch("knowledge_agent.cli.evaluate", return_value=({"failed": 0, "passed": 1, "total": 1}, Path("summary.json"))) as runner:
            with contextlib.redirect_stdout(io.StringIO()):
                main(["evaluate", "--data", "custom.json", "--cases", "normal"])
            self.assertEqual(runner.call_args.args[3], Path("custom.json"))


if __name__ == "__main__":
    unittest.main()

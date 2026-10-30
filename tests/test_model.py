import io
import json
import socket
import unittest
import urllib.error
from unittest.mock import patch

from knowledge_agent.config import ModelConfig
from knowledge_agent.model import LiveModel, ModelError


class ModelTests(unittest.TestCase):
    def test_missing_key_no_network(self):
        with patch("urllib.request.urlopen") as request:
            with self.assertRaises(ModelError) as result:
                LiveModel(ModelConfig(api_key="")).complete([], [])
            self.assertEqual(result.exception.code, "missing_api_key")
            request.assert_not_called()

    def test_timeout_is_explicit(self):
        with patch("urllib.request.urlopen", side_effect=socket.timeout()):
            with self.assertRaises(ModelError) as result:
                LiveModel(ModelConfig(api_key="SYNTHETIC_TEST_KEY")).complete([], [])
            self.assertEqual(result.exception.code, "timeout")

    def test_http_error_redacts_key(self):
        error = urllib.error.HTTPError("https://example.invalid", 403, "denied", {}, io.BytesIO(b"SYNTHETIC_TEST_KEY denied"))
        with patch("urllib.request.urlopen", side_effect=error):
            with self.assertRaises(ModelError) as result:
                LiveModel(ModelConfig(api_key="SYNTHETIC_TEST_KEY")).complete([], [])
            self.assertNotIn("SYNTHETIC_TEST_KEY", str(result.exception))
            self.assertIn("REDACTED", str(result.exception))

    def test_response_discards_internal_reasoning_and_checks_payload(self):
        raw = {"id": "test-request", "model": "test-model", "choices": [{"message": {
            "role": "assistant", "content": "public result", "reasoning_content": "DO_NOT_PERSIST"}}], "usage": {"total_tokens": 7}}
        with patch("urllib.request.urlopen", return_value=io.BytesIO(json.dumps(raw).encode())) as request:
            output = LiveModel(ModelConfig(api_key="SYNTHETIC_TEST_KEY")).complete([], [])
            self.assertNotIn("reasoning_content", output["message"])
            self.assertEqual(output["usage"]["total_tokens"], 7)
            body = json.loads(request.call_args.args[0].data)
            self.assertFalse(body["stream"])
            self.assertFalse(body["enable_thinking"])

    def test_malformed_response_is_explicit(self):
        for data in (b"not json", b"{}", b'{"choices": []}'):
            with self.subTest(data=data), patch("urllib.request.urlopen", return_value=io.BytesIO(data)):
                with self.assertRaises(ModelError) as result:
                    LiveModel(ModelConfig(api_key="SYNTHETIC_TEST_KEY")).complete([], [])
                self.assertEqual(result.exception.code, "invalid_response")

    def test_config_repr_has_no_secret_and_http_rejected(self):
        config = ModelConfig(api_key="SYNTHETIC_TEST_KEY", base_url="http://example.invalid")
        self.assertNotIn("SYNTHETIC_TEST_KEY", repr(config))
        with self.assertRaises(ModelError):
            LiveModel(config).complete([], [])


if __name__ == "__main__":
    unittest.main()

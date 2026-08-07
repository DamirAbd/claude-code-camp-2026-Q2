import io
import json
import unittest
import urllib.error
from unittest.mock import patch

from boukensha import ApiError, Client


class FakeBuilder:
    url = "https://example.test/api"
    headers = {"Content-Type": "application/json"}

    def to_api_payload(self, *, max_output_tokens=1024):
        return {"max_output_tokens": max_output_tokens}


class FakeResponse:
    def __init__(self, body: bytes):
        self._body = body

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def read(self):
        return self._body


def http_error(code):
    return urllib.error.HTTPError(
        "https://example.test/api", code, "error", {}, io.BytesIO(b"boom")
    )


class ClientTest(unittest.TestCase):
    def setUp(self):
        self.client = Client(FakeBuilder())
        sleep_patcher = patch("time.sleep")
        sleep_patcher.start()
        self.addCleanup(sleep_patcher.stop)

    @patch("urllib.request.urlopen")
    def test_returns_parsed_json_on_success(self, mock_urlopen):
        mock_urlopen.return_value = FakeResponse(json.dumps({"ok": True}).encode())
        self.assertEqual(self.client.call(), {"ok": True})

    @patch("urllib.request.urlopen")
    def test_retries_retryable_status_then_succeeds(self, mock_urlopen):
        mock_urlopen.side_effect = [
            http_error(429),
            FakeResponse(json.dumps({"ok": True}).encode()),
        ]
        self.assertEqual(self.client.call(), {"ok": True})
        self.assertEqual(mock_urlopen.call_count, 2)

    @patch("urllib.request.urlopen")
    def test_raises_api_error_after_exhausting_retries(self, mock_urlopen):
        mock_urlopen.side_effect = [http_error(500) for _ in range(4)]
        with self.assertRaisesRegex(ApiError, r"after 4 attempts \(500\): boom"):
            self.client.call()
        self.assertEqual(mock_urlopen.call_count, 4)

    @patch("urllib.request.urlopen")
    def test_raises_immediately_on_non_retryable_status(self, mock_urlopen):
        mock_urlopen.side_effect = [http_error(400)]
        with self.assertRaisesRegex(ApiError, r"after 1 attempt \(400\): boom"):
            self.client.call()
        self.assertEqual(mock_urlopen.call_count, 1)

    @patch("urllib.request.urlopen")
    def test_retries_transient_connection_error_then_succeeds(self, mock_urlopen):
        mock_urlopen.side_effect = [
            ConnectionError("reset"),
            FakeResponse(json.dumps({"ok": True}).encode()),
        ]
        self.assertEqual(self.client.call(), {"ok": True})
        self.assertEqual(mock_urlopen.call_count, 2)

    @patch("urllib.request.urlopen")
    def test_raises_api_error_after_exhausting_transient_retries(self, mock_urlopen):
        mock_urlopen.side_effect = [ConnectionError("reset") for _ in range(4)]
        with self.assertRaisesRegex(ApiError, r"after 4 attempts: ConnectionError"):
            self.client.call()
        self.assertEqual(mock_urlopen.call_count, 4)


if __name__ == "__main__":
    unittest.main()

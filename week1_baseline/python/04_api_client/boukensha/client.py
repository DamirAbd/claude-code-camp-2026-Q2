import json
import ssl
import time
import urllib.error
import urllib.request
from typing import Any

from .errors import ApiError


class Client:
    RETRYABLE_STATUS_CODES = {408, 409, 429, 500, 502, 503, 504}
    TRANSIENT_ERRORS = (TimeoutError, ConnectionError, ssl.SSLError, urllib.error.URLError)
    MAX_RETRIES = 3
    BASE_RETRY_DELAY = 0.5

    def __init__(self, builder: Any):
        self.builder = builder

    def call(self, *, max_output_tokens: int = 1024) -> dict[str, Any]:
        body = json.dumps(
            self.builder.to_api_payload(max_output_tokens=max_output_tokens)
        ).encode("utf-8")

        attempts = 0
        while True:
            attempts += 1
            request = urllib.request.Request(
                self.builder.url, data=body, headers=self.builder.headers, method="POST"
            )

            try:
                with urllib.request.urlopen(request) as response:
                    return json.loads(response.read())
            except urllib.error.HTTPError as error:
                if error.code in self.RETRYABLE_STATUS_CODES and attempts <= self.MAX_RETRIES:
                    time.sleep(self._retry_delay(attempts))
                    continue
                suffix = "" if attempts == 1 else "s"
                body_text = error.read().decode("utf-8", errors="replace")
                raise ApiError(
                    f"API request failed after {attempts} attempt{suffix} "
                    f"({error.code}): {body_text}"
                ) from error
            except self.TRANSIENT_ERRORS as error:
                if attempts > self.MAX_RETRIES:
                    raise ApiError(
                        f"API request failed after {attempts} attempts: "
                        f"{type(error).__name__}: {error}"
                    ) from error
                time.sleep(self._retry_delay(attempts))

    def _retry_delay(self, attempt: int) -> float:
        return self.BASE_RETRY_DELAY * (2 ** (attempt - 1))

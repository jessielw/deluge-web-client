from typing import Optional


class MockResponse:
    """Mock to simulate a requests.Response object"""

    def __init__(
        self,
        json_data: Optional[dict] = {},
        ok: Optional[bool] = None,
        status_code: Optional[int] = None,
        reason: Optional[str] = None,
    ):
        self.json_data = json_data
        self.ok = ok
        self.status_code = status_code
        self.reason = reason

    def json(self):
        return self.json_data

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

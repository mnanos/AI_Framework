import json
import logging

from app.observability.logging import JsonFormatter


def test_json_formatter_emits_structured_log() -> None:
    record = logging.LogRecord(
        name="tests",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="hello",
        args=(),
        exc_info=None,
    )
    record.run_id = "run-1"

    payload = json.loads(JsonFormatter().format(record))

    assert payload["level"] == "info"
    assert payload["message"] == "hello"
    assert payload["run_id"] == "run-1"
    assert "timestamp" in payload

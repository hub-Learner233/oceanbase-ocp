import json

from ansible_collections.oceanbase.ocp.plugins.module_utils.logger import OCPLogger, redact


def test_redact_nested_sensitive_values():
    result = redact({
        "password": "secret",
        "nested": {"accessKeySecret": "sk", "safe": 1},
        "headers": {"Authorization": "Basic abc"},
        "items": [{"token": "token"}],
    })
    assert result["password"] == "***"
    assert result["nested"]["accessKeySecret"] == "***"
    assert result["nested"]["safe"] == 1
    assert result["headers"]["Authorization"] == "***"
    assert result["items"][0]["token"] == "***"


def test_json_file_logger_writes_redacted_record(tmp_path):
    path = tmp_path / "ocp.log"
    logger = OCPLogger(name="test", log_file=str(path), log_level="DEBUG")
    logger.info("request", password="secret", path="/api/v2/info")
    record = json.loads(path.read_text(encoding="utf-8").splitlines()[0])
    assert record["level"] == "INFO"
    assert record["message"] == "request"
    assert record["fields"]["password"] == "***"
    assert record["fields"]["path"] == "/api/v2/info"

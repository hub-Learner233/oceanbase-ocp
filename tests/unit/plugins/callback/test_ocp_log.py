import json

from ansible_collections.oceanbase.ocp.plugins.callback.ocp_log import CallbackModule


class Host(object):
    name = "localhost"


class Task(object):
    action = "oceanbase.ocp.ocp_info"

    def get_path(self):
        return "playbook.yml:1"


def test_callback_writes_redacted_task_result(tmp_path):
    log_file = tmp_path / "callback.jsonl"
    callback = CallbackModule()
    callback._plugin_options = {"log_file": str(log_file), "log_level": "INFO"}
    callback.v2_runner_on_ok(type("Result", (), {
        "_host": Host(), "_task": Task(), "_result": {"changed": False, "password": "VALUE_SPECIFIED_IN_NO_LOG_PARAMETER"},
    })())
    record = json.loads(log_file.read_text(encoding="utf-8").splitlines()[0])
    assert record["event"] == "task_result"
    assert record["host"] == "localhost"
    assert record["status"] == "ok"
    assert record["result"]["password"] == "***"

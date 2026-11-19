from ansible_collections.oceanbase.ocp.plugins.module_utils import module as module_helpers
from ansible_collections.oceanbase.ocp.plugins.module_utils.module import maybe_wait


class Response(object):
    body = {"successful": True, "data": {"id": 8, "status": "RUNNING"}}


class Client(object):
    def __init__(self):
        self.waited = []

    def get_data(self, path):
        self.waited.append(path)
        return {"id": 8, "status": "SUCCESSFUL"}


def test_maybe_wait_returns_completed_task():
    client = Client()
    task = maybe_wait(client, Response(), wait=True, timeout=1, interval=0)
    assert task["status"] == "SUCCESSFUL"
    assert client.waited == ["/api/v2/tasks/instances/8"]


def test_maybe_wait_disabled_returns_none():
    client = Client()
    assert maybe_wait(client, Response(), wait=False, timeout=1, interval=0) is None


def test_run_module_supports_modules_without_name(monkeypatch):
    names = []

    class Module(object):
        params = {}

        def exit_json(self, **result):
            self.result = result

    def fake_create_client(module, name):
        names.append(name)
        return object()

    monkeypatch.setattr(module_helpers, "create_client", fake_create_client)
    module = Module()
    module_helpers.run_module(module, lambda current_module, client: {"changed": False})
    assert names == ["ocp.module"]
    assert module.result == {"changed": False}

import pytest

from ansible_collections.oceanbase.ocp.plugins.module_utils.tasks import OCPTaskError, extract_task_id, wait_for_task


class Client(object):
    def __init__(self, states):
        self.states = iter(states)
        self.paths = []

    def get_data(self, path, query=None):
        self.paths.append(path)
        return {"id": 7, "status": next(self.states)}


def test_extract_task_id_from_async_response():
    assert extract_task_id({"data": {"id": 42, "status": "RUNNING"}}) == 42
    assert extract_task_id({"data": {"contents": []}}) is None


def test_wait_for_task_polls_until_successful():
    client = Client(["RUNNING", "SUCCESSFUL"])
    result = wait_for_task(client, 7, timeout=10, interval=0, sleep=lambda _: None)
    assert result["status"] == "SUCCESSFUL"
    assert client.paths == ["/api/v2/tasks/instances/7"] * 2


def test_wait_for_task_raises_on_failed_status():
    with pytest.raises(OCPTaskError, match="FAILED"):
        wait_for_task(Client(["FAILED"]), 7, timeout=10, interval=0, sleep=lambda _: None)


def test_wait_for_task_times_out():
    clock = [0]

    def sleep(seconds):
        clock[0] += seconds

    with pytest.raises(OCPTaskError, match="timed out"):
        wait_for_task(Client(["RUNNING"] * 4), 7, timeout=2, interval=1, sleep=sleep, monotonic=lambda: clock[0])

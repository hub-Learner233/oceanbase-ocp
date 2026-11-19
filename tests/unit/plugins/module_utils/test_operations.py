from ansible_collections.oceanbase.ocp.plugins.module_utils.operations import (
    cluster_action,
    ensure_cluster,
    ensure_tenant,
    push_alarm,
)


class Response(object):
    def __init__(self, body):
        self.body = body


class Client(object):
    def __init__(self, cluster=None, tenant=None):
        self.cluster = cluster
        self.tenant = tenant
        self.calls = []

    def get_cluster(self, name):
        return self.cluster

    def request(self, method, path, body=None):
        self.calls.append((method, path, body))
        return Response({"successful": True, "data": {"id": 9, "status": "RUNNING"}})


def test_cluster_present_existing_is_unchanged(monkeypatch):
    client = Client(cluster={"id": 1, "name": "prod"})
    monkeypatch.setattr("ansible_collections.oceanbase.ocp.plugins.module_utils.operations.get_cluster", lambda *a, **k: client.cluster)
    result = ensure_cluster(client, "prod", "present", {"name": "prod"}, False)
    assert result["changed"] is False
    assert result["resource"]["id"] == 1
    assert client.calls == []


def test_cluster_present_missing_check_mode_does_not_post(monkeypatch):
    client = Client()
    monkeypatch.setattr("ansible_collections.oceanbase.ocp.plugins.module_utils.operations.get_cluster", lambda *a, **k: None)
    result = ensure_cluster(client, "prod", "present", {"type": "PRIMARY"}, True)
    assert result["changed"] is True
    assert client.calls == []


def test_cluster_absent_existing_deletes_by_id(monkeypatch):
    client = Client(cluster={"id": 1, "name": "prod", "status": "RUNNING"})
    monkeypatch.setattr("ansible_collections.oceanbase.ocp.plugins.module_utils.operations.get_cluster", lambda *a, **k: client.cluster)
    result = ensure_cluster(client, "prod", "absent", None, False)
    assert result["changed"] is True
    assert client.calls == [("DELETE", "/api/v2/ob/clusters/1", None)]


def test_tenant_create_adds_name_to_native_definition(monkeypatch):
    client = Client()
    monkeypatch.setattr("ansible_collections.oceanbase.ocp.plugins.module_utils.operations.get_tenant", lambda *a, **k: None)
    result = ensure_tenant(client, 1, "app", "present", {"mode": "MYSQL"}, False)
    assert result["changed"] is True
    assert client.calls[0][2] == {"mode": "MYSQL", "name": "app"}


def test_cluster_start_running_is_noop():
    client = Client(cluster={"id": 1, "status": "RUNNING"})
    result = cluster_action(client, client.cluster, "start", None, False)
    assert result["changed"] is False
    assert client.calls == []


def test_cluster_restart_sends_action_and_body():
    client = Client(cluster={"id": 1, "status": "RUNNING"})
    result = cluster_action(client, client.cluster, "restart", {"force": True}, False)
    assert result["changed"] is True
    assert client.calls == [("POST", "/api/v2/ob/clusters/1/restart", {"force": True})]


def test_alarm_check_mode_does_not_post():
    client = Client()
    result = push_alarm(client, {"alarmType": "test"}, True)
    assert result["changed"] is True
    assert client.calls == []

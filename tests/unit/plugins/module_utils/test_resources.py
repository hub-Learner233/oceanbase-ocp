import pytest

from ansible_collections.oceanbase.ocp.plugins.module_utils.resources import (
    OCPResourceError,
    find_exact,
    get_cluster,
    get_tenant,
)


class Client(object):
    def __init__(self, resources):
        self.resources = resources
        self.queries = []

    def list_all(self, path, query=None):
        self.queries.append((path, query))
        return self.resources, {"totalElements": len(self.resources)}

    def get_data(self, path):
        return self.resources[0] if self.resources else None


def test_find_exact_ignores_partial_matches():
    resources = [{"name": "db"}, {"name": "db-old"}]
    assert find_exact(resources, "db", "cluster") == resources[0]
    assert find_exact(resources, "missing", "cluster") is None


def test_find_exact_rejects_duplicate_names():
    with pytest.raises(OCPResourceError, match="Multiple cluster"):
        find_exact([{"name": "db"}, {"name": "db"}], "db", "cluster")


def test_get_cluster_uses_name_filter_then_exact_match():
    client = Client([{"id": 1, "name": "prod"}])
    assert get_cluster(client, name="prod")["id"] == 1
    assert client.queries[0] == ("/api/v2/ob/clusters", {"name": "prod"})


def test_get_tenant_uses_cluster_scoped_path():
    client = Client([{"id": 2, "name": "app"}])
    assert get_tenant(client, 1, name="app")["id"] == 2
    assert client.queries[0][0] == "/api/v2/ob/clusters/1/tenants"


def test_required_missing_resource_raises():
    with pytest.raises(OCPResourceError, match="not found"):
        get_cluster(Client([]), name="missing", required=True)

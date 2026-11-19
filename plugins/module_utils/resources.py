from __future__ import absolute_import, division, print_function

__metaclass__ = type


class OCPResourceError(Exception):
    pass


def find_exact(resources, name, resource_type):
    matches = [item for item in resources if item.get("name") == name]
    if len(matches) > 1:
        raise OCPResourceError("Multiple %s resources named %r were found; use an ID instead" % (resource_type, name))
    return matches[0] if matches else None


def get_cluster(client, name=None, cluster_id=None, required=False):
    if cluster_id is not None:
        resource = client.get_data("/api/v2/ob/clusters/%s" % cluster_id)
    else:
        resources, unused_page = client.list_all("/api/v2/ob/clusters", query={"name": name})
        resource = find_exact(resources, name, "cluster")
    if required and not resource:
        raise OCPResourceError("OceanBase cluster %r not found" % (name or cluster_id))
    return resource


def get_tenant(client, cluster_id, name=None, tenant_id=None, required=False):
    if tenant_id is not None:
        resource = client.get_data("/api/v2/ob/clusters/%s/tenants/%s" % (cluster_id, tenant_id))
    else:
        resources, unused_page = client.list_all("/api/v2/ob/clusters/%s/tenants" % cluster_id, query={"name": name})
        resource = find_exact(resources, name, "tenant")
    if required and not resource:
        raise OCPResourceError("OceanBase tenant %r not found in cluster %s" % (name or tenant_id, cluster_id))
    return resource


def resolve_cluster_id(client, name=None, cluster_id=None):
    if cluster_id is not None:
        return cluster_id
    cluster = get_cluster(client, name=name, required=True)
    return cluster["id"]

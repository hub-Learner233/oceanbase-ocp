from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.oceanbase.ocp.plugins.module_utils.resources import get_cluster, get_tenant


def ensure_cluster(client, name, state, definition, check_mode):
    existing = get_cluster(client, name=name)
    if state == "present":
        if existing:
            return {"changed": False, "resource": existing, "response": None}
        if check_mode:
            return {"changed": True, "resource": None, "response": None}
        payload = dict(definition or {})
        payload["name"] = name
        response = client.request("POST", "/api/v2/ob/clusters", body=payload)
        return {"changed": True, "resource": None, "response": response}
    if not existing:
        return {"changed": False, "resource": None, "response": None}
    if check_mode:
        return {"changed": True, "resource": existing, "response": None}
    response = client.request("DELETE", "/api/v2/ob/clusters/%s" % existing["id"])
    return {"changed": True, "resource": existing, "response": response}


def ensure_tenant(client, cluster_id, name, state, definition, check_mode):
    existing = get_tenant(client, cluster_id, name=name)
    path = "/api/v2/ob/clusters/%s/tenants" % cluster_id
    if state == "present":
        if existing:
            return {"changed": False, "resource": existing, "response": None}
        if check_mode:
            return {"changed": True, "resource": None, "response": None}
        payload = dict(definition or {})
        payload["name"] = name
        response = client.request("POST", path, body=payload)
        return {"changed": True, "resource": None, "response": response}
    if not existing:
        return {"changed": False, "resource": None, "response": None}
    if check_mode:
        return {"changed": True, "resource": existing, "response": None}
    response = client.request("DELETE", path + "/%s" % existing["id"])
    return {"changed": True, "resource": existing, "response": response}


def cluster_action(client, cluster, action, parameters, check_mode):
    status = str(cluster.get("status", "")).upper()
    if (action == "start" and status == "RUNNING") or (action == "stop" and status == "STOPPED"):
        return {"changed": False, "resource": cluster, "response": None}
    if check_mode:
        return {"changed": True, "resource": cluster, "response": None}
    response = client.request(
        "POST", "/api/v2/ob/clusters/%s/%s" % (cluster["id"], action), body=parameters,
    )
    return {"changed": True, "resource": cluster, "response": response}


def push_alarm(client, event, check_mode):
    if check_mode:
        return {"changed": True, "response": None}
    response = client.request("POST", "/api/v2/alarm/alarms", body=event)
    return {"changed": True, "response": response}

#!/usr/bin/python
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
module: ocp_cluster_info
short_description: Query OceanBase clusters and OBServer nodes through OCP
version_added: 0.1.0
author:
  - OceanBase OCP Collection contributors (!UNKNOWN)
description: Query cluster lists, exact cluster details and optional OBServer nodes.
extends_documentation_fragment: [oceanbase.ocp.connection, oceanbase.ocp.logging]
options:
  name:
    description: Exact OceanBase cluster name.
    type: str
  cluster_id:
    description: Cluster ID on the OCP side.
    type: int
  query:
    description: Additional official list filters such as C(status), C(sort) and C(withStandby).
    type: dict
    default: {}
  include_servers:
    description: Include OBServers when querying one cluster.
    type: bool
    default: false
"""
EXAMPLES = r"""
- oceanbase.ocp.ocp_cluster_info:
    base_url: "{{ ocp_url }}"
    username: "{{ ocp_username }}"
    password: "{{ ocp_password }}"
    name: production
    include_servers: true
  register: cluster
"""
RETURN = r"""
clusters:
  description: OceanBase cluster list.
  type: list
  returned: success
cluster:
  description: Selected OceanBase cluster.
  type: dict
  returned: when one cluster is selected
servers:
  description: OBServer nodes in the selected cluster.
  type: list
  returned: when include_servers=true for one cluster
page:
  description: Final OCP pagination metadata.
  type: dict
  returned: for list queries
"""

from ansible_collections.oceanbase.ocp.plugins.module_utils.module import create_module, run_module
from ansible_collections.oceanbase.ocp.plugins.module_utils.resources import get_cluster


def handler(module, client):
    params = module.params
    if params.get("name") or params.get("cluster_id") is not None:
        cluster = get_cluster(client, name=params.get("name"), cluster_id=params.get("cluster_id"), required=True)
        servers = None
        if params["include_servers"]:
            servers, unused_page = client.list_all("/api/v2/ob/clusters/%s/servers" % cluster["id"], query=params["query"])
        return {"changed": False, "clusters": [cluster], "cluster": cluster, "servers": servers}
    clusters, page = client.list_all("/api/v2/ob/clusters", query=params["query"])
    return {"changed": False, "clusters": clusters, "page": page}


def main():
    module = create_module(dict(
        name=dict(type="str"), cluster_id=dict(type="int"), query=dict(type="dict", default={}),
        include_servers=dict(type="bool", default=False),
    ), mutually_exclusive=[["name", "cluster_id"]])
    run_module(module, handler)


if __name__ == "__main__":
    main()

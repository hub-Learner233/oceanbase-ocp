#!/usr/bin/python
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
module: ocp_host_info
short_description: Query hosts managed by OCP
version_added: 0.1.0
author:
  - OceanBase OCP Collection contributors (!UNKNOWN)
description: Uses C(GET /api/v2/compute/hosts) and automatic pagination.
extends_documentation_fragment: [oceanbase.ocp.connection, oceanbase.ocp.logging]
options:
  host_id:
    description: OCP-side host ID for a detail query.
    type: int
  keyword:
    description: Fuzzy host name, IP or service keyword.
    type: str
  status:
    description: Host states to include.
    type: list
    elements: str
  included_service_type:
    description: Require at least one of these deployed service types.
    type: list
    elements: str
  excluded_service_type:
    description: Exclude hosts with these deployed service types.
    type: list
    elements: str
  query:
    description: Additional native OCP host list filters.
    type: dict
    default: {}
"""
EXAMPLES = r"""
- oceanbase.ocp.ocp_host_info:
    base_url: "{{ ocp_url }}"
    access_key: "{{ ocp_access_key }}"
    secret_key: "{{ ocp_secret_key }}"
    status: [ONLINE, AVAILABLE]
  register: hosts
"""
RETURN = r"""
hosts:
  description: Hosts managed by OCP.
  type: list
  returned: success
host:
  description: Selected host detail.
  type: dict
  returned: when host_id is set
page:
  description: Final OCP pagination metadata.
  type: dict
  returned: for list queries
"""

from ansible_collections.oceanbase.ocp.plugins.module_utils.module import create_module, run_module


def handler(module, client):
    p = module.params
    if p.get("host_id") is not None:
        host = client.get_data("/api/v2/compute/hosts/%s" % p["host_id"])
        return {"changed": False, "hosts": [host], "host": host}
    query = dict(p["query"])
    mapping = {
        "keyword": "keyword", "status": "status",
        "included_service_type": "includedServiceType", "excluded_service_type": "excludedServiceType",
    }
    for source, target in mapping.items():
        if p.get(source) is not None:
            query[target] = p[source]
    hosts, page = client.list_all("/api/v2/compute/hosts", query=query)
    return {"changed": False, "hosts": hosts, "page": page}


def main():
    module = create_module(dict(
        host_id=dict(type="int"), keyword=dict(type="str", no_log=True), status=dict(type="list", elements="str"),
        included_service_type=dict(type="list", elements="str"), excluded_service_type=dict(type="list", elements="str"),
        query=dict(type="dict", default={}),
    ))
    run_module(module, handler)


if __name__ == "__main__":
    main()

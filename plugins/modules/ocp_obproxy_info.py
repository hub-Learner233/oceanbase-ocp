#!/usr/bin/python
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
module: ocp_obproxy_info
short_description: Query OBProxy clusters managed by OCP
version_added: 0.1.0
author:
  - OceanBase OCP Collection contributors (!UNKNOWN)
description: Query OBProxy cluster lists and optionally filter by exact name.
extends_documentation_fragment: [oceanbase.ocp.connection, oceanbase.ocp.logging]
options:
  name:
    description: Exact OBProxy cluster name.
    type: str
  query:
    description: Additional native OCP OBProxy list filters.
    type: dict
    default: {}
"""
EXAMPLES = r"""
- oceanbase.ocp.ocp_obproxy_info:
    base_url: "{{ ocp_url }}"
    access_key: "{{ ocp_access_key }}"
    secret_key: "{{ ocp_secret_key }}"
  register: obproxy_clusters
"""
RETURN = r"""
obproxy_clusters:
  description: OBProxy clusters managed by OCP.
  type: list
  returned: success
page:
  description: Final OCP pagination metadata.
  type: dict
  returned: when supplied by OCP
"""

from ansible_collections.oceanbase.ocp.plugins.module_utils.module import create_module, run_module
from ansible_collections.oceanbase.ocp.plugins.module_utils.resources import find_exact


def handler(module, client):
    resources, page = client.list_all("/api/v2/obproxy/clusters", query=module.params["query"])
    if module.params.get("name"):
        resource = find_exact(resources, module.params["name"], "OBProxy cluster")
        resources = [resource] if resource else []
    return {"changed": False, "obproxy_clusters": resources, "page": page}


def main():
    run_module(create_module(dict(name=dict(type="str"), query=dict(type="dict", default={}))), handler)


if __name__ == "__main__":
    main()

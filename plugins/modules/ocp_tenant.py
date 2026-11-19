#!/usr/bin/python
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
module: ocp_tenant
short_description: Create or delete an OceanBase tenant through OCP
version_added: 0.1.0
author:
  - OceanBase OCP Collection contributors (!UNKNOWN)
description:
  - Ensures that a tenant name is present or absent within one OCP cluster.
  - Creation accepts the target OCP version's native definition; existing tenants are not implicitly updated.
extends_documentation_fragment: [oceanbase.ocp.connection, oceanbase.ocp.logging, oceanbase.ocp.wait]
options:
  cluster_name:
    description: Name of the containing OceanBase cluster.
    type: str
  cluster_id:
    description: OCP-side ID of the containing cluster.
    type: int
  name:
    description: Tenant name.
    type: str
    required: true
  state:
    description: Ensure the tenant is present or absent.
    type: str
    choices: [present, absent]
    default: present
  definition:
    description: Native tenant creation body including C(mode), C(zones), C(primaryZone) and optional C(rootPassword).
    type: dict
    default: {}
"""
EXAMPLES = r"""
- oceanbase.ocp.ocp_tenant:
    base_url: "{{ ocp_url }}"
    access_key: "{{ ocp_access_key }}"
    secret_key: "{{ ocp_secret_key }}"
    cluster_name: production
    name: app
    definition:
      mode: MYSQL
      primaryZone: "zone1"
      charset: utf8mb4
      collation: utf8mb4_general_ci
      whitelist: "%"
      rootPassword: "{{ tenant_root_password }}"
      zones:
        - name: zone1
          replicaType: FULL
          resourcePool: {unitSpecName: S1, unitCount: 1}
  no_log: true
"""
RETURN = r"""
changed:
  description: Whether a tenant operation was required or submitted.
  type: bool
  returned: always
resource:
  description: Existing tenant used for idempotency or deletion.
  type: dict
  returned: when an existing tenant was found
response:
  description: Complete OCP JSON response.
  type: raw
  returned: when OCP was changed
task:
  description: Completed OCP asynchronous task.
  type: dict
  returned: when an asynchronous task was awaited
"""

from ansible_collections.oceanbase.ocp.plugins.module_utils.module import (
    create_module, maybe_wait, response_result, run_module,
)
from ansible_collections.oceanbase.ocp.plugins.module_utils.operations import ensure_tenant
from ansible_collections.oceanbase.ocp.plugins.module_utils.resources import resolve_cluster_id


def handler(module, client):
    p = module.params
    cluster_id = resolve_cluster_id(client, p.get("cluster_name"), p.get("cluster_id"))
    result = ensure_tenant(client, cluster_id, p["name"], p["state"], p["definition"], module.check_mode)
    response = result.pop("response")
    task = maybe_wait(client, response, p["wait"], p["wait_timeout"], p["wait_interval"])
    return response_result(result.pop("changed"), response, task=task, **result)


def main():
    module = create_module(dict(
        cluster_name=dict(type="str"), cluster_id=dict(type="int"), name=dict(type="str", required=True),
        state=dict(type="str", choices=["present", "absent"], default="present"), definition=dict(type="dict", default={}),
    ), include_wait=True, required_one_of=[["cluster_name", "cluster_id"]], mutually_exclusive=[["cluster_name", "cluster_id"]])
    run_module(module, handler)


if __name__ == "__main__":
    main()

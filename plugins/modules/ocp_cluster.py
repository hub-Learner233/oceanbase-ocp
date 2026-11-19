#!/usr/bin/python
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
module: ocp_cluster
short_description: Create or delete an OceanBase cluster through OCP
version_added: 0.1.0
author:
  - OceanBase OCP Collection contributors (!UNKNOWN)
description:
  - Ensures that a cluster name is present or absent.
  - Creation uses the native request body from the target OCP version. Existing clusters are not implicitly updated.
extends_documentation_fragment: [oceanbase.ocp.connection, oceanbase.ocp.logging, oceanbase.ocp.wait]
options:
  name:
    description: Globally unique OceanBase cluster name.
    type: str
    required: true
  state:
    description: Ensure the cluster is present or absent.
    type: str
    choices: [present, absent]
    default: present
  definition:
    description: Native C(POST /api/v2/ob/clusters) body. C(name) is populated from the module parameter.
    type: dict
    default: {}
"""
EXAMPLES = r"""
- oceanbase.ocp.ocp_cluster:
    base_url: "{{ ocp_url }}"
    access_key: "{{ ocp_access_key }}"
    secret_key: "{{ ocp_secret_key }}"
    name: production
    definition:
      type: PRIMARY
      password: "{{ ob_sys_password }}"
      primaryZone: ""
      rpmName: "{{ ob_rpm_name }}"
      zones: "{{ ob_zones }}"
    wait: true
  no_log: true
"""
RETURN = r"""
changed:
  description: Whether a cluster operation was required or submitted.
  type: bool
  returned: always
resource:
  description: Existing cluster used for idempotency or deletion.
  type: dict
  returned: when an existing cluster was found
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
from ansible_collections.oceanbase.ocp.plugins.module_utils.operations import ensure_cluster


def handler(module, client):
    p = module.params
    result = ensure_cluster(client, p["name"], p["state"], p["definition"], module.check_mode)
    response = result.pop("response")
    task = maybe_wait(client, response, p["wait"], p["wait_timeout"], p["wait_interval"])
    return response_result(result.pop("changed"), response, task=task, **result)


def main():
    module = create_module(dict(
        name=dict(type="str", required=True), state=dict(type="str", choices=["present", "absent"], default="present"),
        definition=dict(type="dict", default={}),
    ), include_wait=True)
    run_module(module, handler)


if __name__ == "__main__":
    main()

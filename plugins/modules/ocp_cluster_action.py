#!/usr/bin/python
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
module: ocp_cluster_action
short_description: Start, stop or restart an OceanBase cluster through OCP
version_added: 0.1.0
author:
  - OceanBase OCP Collection contributors (!UNKNOWN)
description:
  - Calls C(POST /api/v2/ob/clusters/{id}/{action}).
  - Starting a running cluster and stopping a stopped cluster are no-ops. Restart always submits a task.
extends_documentation_fragment: [oceanbase.ocp.connection, oceanbase.ocp.logging, oceanbase.ocp.wait]
options:
  name:
    description: Exact OceanBase cluster name.
    type: str
  cluster_id:
    description: OCP-side cluster ID.
    type: int
  action:
    description: Lifecycle action to perform.
    type: str
    choices: [start, stop, restart]
    required: true
  parameters:
    description: Optional native action request body supported by the target OCP version.
    type: dict
"""
EXAMPLES = r"""
- oceanbase.ocp.ocp_cluster_action:
    base_url: "{{ ocp_url }}"
    access_key: "{{ ocp_access_key }}"
    secret_key: "{{ ocp_secret_key }}"
    name: staging
    action: restart
    wait: true
"""
RETURN = r"""
changed:
  description: Whether a lifecycle action was required or submitted.
  type: bool
  returned: always
resource:
  description: Cluster targeted by the lifecycle action.
  type: dict
  returned: success
response:
  description: Complete OCP JSON response.
  type: raw
  returned: when an action was submitted
task:
  description: Completed OCP asynchronous task.
  type: dict
  returned: when an asynchronous task was awaited
"""

from ansible_collections.oceanbase.ocp.plugins.module_utils.module import (
    create_module, maybe_wait, response_result, run_module,
)
from ansible_collections.oceanbase.ocp.plugins.module_utils.operations import cluster_action
from ansible_collections.oceanbase.ocp.plugins.module_utils.resources import get_cluster


def handler(module, client):
    p = module.params
    cluster = get_cluster(client, name=p.get("name"), cluster_id=p.get("cluster_id"), required=True)
    result = cluster_action(client, cluster, p["action"], p.get("parameters"), module.check_mode)
    response = result.pop("response")
    task = maybe_wait(client, response, p["wait"], p["wait_timeout"], p["wait_interval"])
    return response_result(result.pop("changed"), response, task=task, **result)


def main():
    module = create_module(dict(
        name=dict(type="str"), cluster_id=dict(type="int"),
        action=dict(type="str", choices=["start", "stop", "restart"], required=True), parameters=dict(type="dict"),
    ), include_wait=True, required_one_of=[["name", "cluster_id"]], mutually_exclusive=[["name", "cluster_id"]])
    run_module(module, handler)


if __name__ == "__main__":
    main()

#!/usr/bin/python
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
module: ocp_task_info
short_description: Query or wait for OCP asynchronous tasks
version_added: 0.1.0
author:
  - OceanBase OCP Collection contributors (!UNKNOWN)
description: Query OCP task lists, inspect one task or wait for its terminal state.
extends_documentation_fragment: [oceanbase.ocp.connection, oceanbase.ocp.logging, oceanbase.ocp.wait]
options:
  task_id:
    description: OCP task ID for a detail query or wait.
    type: int
  query:
    description: Official task filters including C(status), C(clusterId), C(tenantId), C(name) and C(sort).
    type: dict
    default: {}
  wait:
    description: Wait for the selected task to reach a terminal state.
    type: bool
    default: false
"""
EXAMPLES = r"""
- oceanbase.ocp.ocp_task_info:
    base_url: "{{ ocp_url }}"
    access_key: "{{ ocp_access_key }}"
    secret_key: "{{ ocp_secret_key }}"
    task_id: 4000191
    wait: true
    wait_timeout: 1200
  register: task
"""
RETURN = r"""
tasks:
  description: OCP asynchronous task list.
  type: list
  returned: for list queries
task:
  description: Selected or completed OCP task.
  type: dict
  returned: when task_id is set
page:
  description: Final OCP pagination metadata.
  type: dict
  returned: for list queries
"""

from ansible_collections.oceanbase.ocp.plugins.module_utils.module import create_module, run_module
from ansible_collections.oceanbase.ocp.plugins.module_utils.tasks import wait_for_task


def handler(module, client):
    p = module.params
    if p.get("task_id") is not None:
        if p["wait"]:
            task = wait_for_task(client, p["task_id"], p["wait_timeout"], p["wait_interval"])
        else:
            task = client.get_data("/api/v2/tasks/instances/%s" % p["task_id"])
        return {"changed": False, "task": task}
    tasks, page = client.list_all("/api/v2/tasks/instances", query=p["query"])
    return {"changed": False, "tasks": tasks, "page": page}


def main():
    module = create_module(dict(
        task_id=dict(type="int"), query=dict(type="dict", default={}), wait=dict(type="bool", default=False),
    ), include_wait=True)
    run_module(module, handler)


if __name__ == "__main__":
    main()

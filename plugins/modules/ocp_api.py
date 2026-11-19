#!/usr/bin/python
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
module: ocp_api
short_description: Call any OceanBase OCP Open API endpoint
version_added: 0.1.0
author:
  - OceanBase OCP Collection contributors (!UNKNOWN)
description:
  - Generic REST module for OCP endpoints not covered by a dedicated module.
  - Use the official OCP API reference for the target OCP version.
extends_documentation_fragment: [oceanbase.ocp.connection, oceanbase.ocp.logging, oceanbase.ocp.wait]
options:
  method:
    description: HTTP method to call.
    type: str
    choices: [GET, PUT, POST, DELETE, PATCH, HEAD, OPTIONS]
    default: GET
  path:
    description: Absolute API path, for example C(/api/v2/ob/clusters).
    type: str
    required: true
  query:
    description: Native URL query parameters; list values are encoded as repeated keys.
    type: dict
    default: {}
  body:
    description: Native OCP JSON request body.
    type: raw
  changed:
    description: Override reported change status. By default safe methods are unchanged and others are changed.
    type: bool
  wait:
    description: Wait when the response contains an OCP asynchronous task ID.
    type: bool
    default: false
"""

EXAMPLES = r"""
- name: Query OCP monitor data
  oceanbase.ocp.ocp_api:
    base_url: "{{ ocp_url }}"
    access_key: "{{ ocp_access_key }}"
    secret_key: "{{ ocp_secret_key }}"
    path: /api/v2/monitor/top
    query:
      metrics: host_cpu_total
      maxPoints: 60

- name: Call a version-specific OCP endpoint
  oceanbase.ocp.ocp_api:
    base_url: "{{ ocp_url }}"
    username: "{{ ocp_username }}"
    password: "{{ ocp_password }}"
    method: POST
    path: /api/v2/ob/clusters/1/tenants/2/switchover
    wait: true
"""

RETURN = r"""
changed:
  description: Whether the API call represents a change.
  type: bool
  returned: always
data:
  description: Business data unwrapped from the OCP response envelope.
  returned: when a request was executed
  type: raw
response:
  description: Complete OCP JSON response.
  returned: when a request was executed
  type: raw
task:
  description: Completed asynchronous task when C(wait=true) and a task ID was returned.
  type: dict
  returned: when applicable
request:
  description: Planned request without a body, returned for mutating calls in check mode.
  type: dict
  returned: in check mode for mutating methods
"""

from ansible_collections.oceanbase.ocp.plugins.module_utils.module import (
    create_module, maybe_wait, response_result, run_module,
)

SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}


def handler(module, client):
    method = module.params["method"]
    path = module.params["path"]
    query = module.params["query"]
    body = module.params.get("body")
    inferred_changed = method not in SAFE_METHODS
    changed = module.params["changed"] if module.params.get("changed") is not None else inferred_changed
    if module.check_mode and inferred_changed:
        return {"changed": changed, "request": {"method": method, "path": path, "query": query}}
    response = client.request(method, path, query=query, body=body)
    task = maybe_wait(client, response, module.params["wait"], module.params["wait_timeout"], module.params["wait_interval"])
    return response_result(changed, response, data=response.data, task=task)


def main():
    module = create_module(dict(
        method=dict(type="str", choices=["GET", "PUT", "POST", "DELETE", "PATCH", "HEAD", "OPTIONS"], default="GET"),
        path=dict(type="str", required=True), query=dict(type="dict", default={}),
        body=dict(type="raw"), changed=dict(type="bool"), wait=dict(type="bool", default=False),
    ), include_wait=True)
    run_module(module, handler)


if __name__ == "__main__":
    main()

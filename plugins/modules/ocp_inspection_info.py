#!/usr/bin/python
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
module: ocp_inspection_info
short_description: Query OCP inspection task reports
version_added: 0.1.0
author:
  - OceanBase OCP Collection contributors (!UNKNOWN)
description: Calls C(GET /api/v2/inspection/task).
extends_documentation_fragment: [oceanbase.ocp.connection, oceanbase.ocp.logging]
options:
  name:
    description: Inspection object name keyword.
    type: str
  task_states:
    description: OCP inspection task state filter.
    type: str
  inspection_object_types:
    description: Object types such as OB_CLUSTER, OB_TENANT, HOST or OB_PROXY.
    type: list
    elements: str
  tags:
    description: OCP inspection scenario tag IDs.
    type: list
    elements: int
  query:
    description: Additional native OCP inspection filters.
    type: dict
    default: {}
"""
EXAMPLES = r"""
- oceanbase.ocp.ocp_inspection_info:
    base_url: "{{ ocp_url }}"
    access_key: "{{ ocp_access_key }}"
    secret_key: "{{ ocp_secret_key }}"
    task_states: FAILED
  register: failed_inspections
"""
RETURN = r"""
inspections:
  description: OCP inspection reports and risk counts.
  type: list
  returned: success
page:
  description: Final OCP pagination metadata.
  type: dict
  returned: success
"""

from ansible_collections.oceanbase.ocp.plugins.module_utils.module import create_module, run_module


def handler(module, client):
    p = module.params
    query = dict(p["query"])
    for source, target in (("name", "name"), ("task_states", "taskStates"), ("inspection_object_types", "inspectionObjectTypes"), ("tags", "tags")):
        if p.get(source) is not None:
            query[target] = p[source]
    inspections, page = client.list_all("/api/v2/inspection/task", query=query)
    return {"changed": False, "inspections": inspections, "page": page}


def main():
    module = create_module(dict(
        name=dict(type="str"), task_states=dict(type="str"),
        inspection_object_types=dict(type="list", elements="str"), tags=dict(type="list", elements="int"),
        query=dict(type="dict", default={}),
    ))
    run_module(module, handler)


if __name__ == "__main__":
    main()

#!/usr/bin/python
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
module: ocp_alarm
short_description: Push an external alarm event to OCP
version_added: 0.1.0
author:
  - OceanBase OCP Collection contributors (!UNKNOWN)
description: Calls C(POST /api/v2/alarm/alarms) with a native alarm event.
extends_documentation_fragment: [oceanbase.ocp.connection, oceanbase.ocp.logging]
options:
  event:
    description: Alarm object containing C(alarmType), C(labels), C(target) and other fields supported by OCP.
    type: dict
    required: true
"""
EXAMPLES = r"""
- oceanbase.ocp.ocp_alarm:
    base_url: "{{ ocp_url }}"
    access_key: "{{ ocp_access_key }}"
    secret_key: "{{ ocp_secret_key }}"
    event:
      alarmType: backup_failed
      labels: {cluster: production, source: ansible}
      target: production
"""
RETURN = r"""
changed:
  description: Always true for a submitted or planned alarm event.
  type: bool
  returned: always
response:
  description: Complete OCP JSON response.
  type: raw
  returned: when the event was submitted
"""

from ansible_collections.oceanbase.ocp.plugins.module_utils.module import create_module, response_result, run_module
from ansible_collections.oceanbase.ocp.plugins.module_utils.operations import push_alarm


def handler(module, client):
    result = push_alarm(client, module.params["event"], module.check_mode)
    return response_result(result["changed"], result["response"])


def main():
    run_module(create_module(dict(event=dict(type="dict", required=True))), handler)


if __name__ == "__main__":
    main()

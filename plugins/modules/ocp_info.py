#!/usr/bin/python
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
module: ocp_info
short_description: Get OCP application version and build information
version_added: 0.1.0
author:
  - OceanBase OCP Collection contributors (!UNKNOWN)
description: Calls C(GET /api/v2/info).
extends_documentation_fragment: [oceanbase.ocp.connection, oceanbase.ocp.logging]
"""
EXAMPLES = r"""
- oceanbase.ocp.ocp_info:
    base_url: "{{ ocp_url }}"
    access_key: "{{ ocp_access_key }}"
    secret_key: "{{ ocp_secret_key }}"
  register: ocp_application
"""
RETURN = r"""
info:
  type: dict
  returned: success
  description: OCP application information.
response:
  description: Complete OCP JSON response.
  type: raw
  returned: success
"""

from ansible_collections.oceanbase.ocp.plugins.module_utils.module import create_module, response_result, run_module


def handler(module, client):
    response = client.request("GET", "/api/v2/info")
    return response_result(False, response, info=response.data)


def main():
    run_module(create_module(), handler)


if __name__ == "__main__":
    main()

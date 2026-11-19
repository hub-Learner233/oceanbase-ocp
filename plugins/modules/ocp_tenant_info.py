#!/usr/bin/python
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
module: ocp_tenant_info
short_description: Query OceanBase tenants through OCP
version_added: 0.1.0
author:
  - OceanBase OCP Collection contributors (!UNKNOWN)
description: Query tenant lists or exact tenant details within an OceanBase cluster.
extends_documentation_fragment: [oceanbase.ocp.connection, oceanbase.ocp.logging]
options:
  cluster_name:
    description: Name of the containing OceanBase cluster.
    type: str
  cluster_id:
    description: OCP-side ID of the containing cluster.
    type: int
  name:
    description: Exact tenant name.
    type: str
  tenant_id:
    description: OCP-side tenant ID.
    type: int
  query:
    description: Additional native OCP tenant list filters.
    type: dict
    default: {}
"""
EXAMPLES = r"""
- oceanbase.ocp.ocp_tenant_info:
    base_url: "{{ ocp_url }}"
    access_key: "{{ ocp_access_key }}"
    secret_key: "{{ ocp_secret_key }}"
    cluster_name: production
    name: app
  register: tenant
"""
RETURN = r"""
tenants:
  description: OceanBase tenant list.
  type: list
  returned: success
tenant:
  description: Selected OceanBase tenant.
  type: dict
  returned: when one tenant is selected
page:
  description: Final OCP pagination metadata.
  type: dict
  returned: for list queries
"""

from ansible_collections.oceanbase.ocp.plugins.module_utils.module import create_module, run_module
from ansible_collections.oceanbase.ocp.plugins.module_utils.resources import get_tenant, resolve_cluster_id


def handler(module, client):
    p = module.params
    cluster_id = resolve_cluster_id(client, p.get("cluster_name"), p.get("cluster_id"))
    if p.get("name") or p.get("tenant_id") is not None:
        tenant = get_tenant(client, cluster_id, name=p.get("name"), tenant_id=p.get("tenant_id"), required=True)
        return {"changed": False, "tenants": [tenant], "tenant": tenant}
    tenants, page = client.list_all("/api/v2/ob/clusters/%s/tenants" % cluster_id, query=p["query"])
    return {"changed": False, "tenants": tenants, "page": page}


def main():
    module = create_module(dict(
        cluster_name=dict(type="str"), cluster_id=dict(type="int"), name=dict(type="str"),
        tenant_id=dict(type="int"), query=dict(type="dict", default={}),
    ), required_one_of=[["cluster_name", "cluster_id"]], mutually_exclusive=[["cluster_name", "cluster_id"], ["name", "tenant_id"]])
    run_module(module, handler)


if __name__ == "__main__":
    main()

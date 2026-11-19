from __future__ import absolute_import, division, print_function
__metaclass__ = type


class ModuleDocFragment(object):
    DOCUMENTATION = r"""
options:
  base_url:
    description: OCP base URL, for example C(https://ocp.example.com:8080).
    type: str
    required: true
  username:
    description: OCP username for HTTP Basic authentication.
    type: str
  password:
    description: OCP password for HTTP Basic authentication. Prefer Ansible Vault.
    type: str
  access_key:
    description: OCP AccessKey ID. Recommended over Basic authentication.
    type: str
  secret_key:
    description: OCP AccessKey Secret. Prefer Ansible Vault.
    type: str
  validate_certs:
    description: Validate TLS certificates.
    type: bool
    default: true
  timeout:
    description: HTTP request timeout in seconds.
    type: int
    default: 30
  retries:
    description: Retries for connection errors and retryable responses on idempotent methods.
    type: int
    default: 3
  retry_backoff:
    description: Initial exponential retry backoff in seconds.
    type: float
    default: 1.0
  accept_language:
    description: Value of the C(Accept-Language) request header.
    type: str
    default: zh-CN
  origin:
    description: Value of C(x-ocp-origin), included in AK/SK signatures.
    type: str
    default: ansible-oceanbase.ocp
  headers:
    description: Additional HTTP headers. Sensitive values are redacted from logs.
    type: dict
    default: {}
notes:
  - Supply either C(username) and C(password), or C(access_key) and C(secret_key).
  - Environment fallbacks are OCP_URL, OCP_USERNAME, OCP_PASSWORD, OCP_ACCESS_KEY and OCP_SECRET_KEY when registered by the playbook.
"""

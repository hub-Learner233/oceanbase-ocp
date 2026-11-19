from __future__ import absolute_import, division, print_function
__metaclass__ = type


class ModuleDocFragment(object):
    DOCUMENTATION = r"""
options:
  log_file:
    description: Optional JSON Lines log file on the module execution host.
    type: str
  log_level:
    description: Minimum log level.
    type: str
    choices: [DEBUG, INFO, WARNING, ERROR]
    default: INFO
  log_request_body:
    description: Include redacted request bodies in debug logs. Responses are never logged by default.
    type: bool
    default: false
"""

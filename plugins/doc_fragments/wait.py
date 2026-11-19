from __future__ import absolute_import, division, print_function
__metaclass__ = type


class ModuleDocFragment(object):
    DOCUMENTATION = r"""
options:
  wait:
    description: Wait for an OCP asynchronous task when the response contains a task ID.
    type: bool
    default: true
  wait_timeout:
    description: Maximum task wait time in seconds.
    type: int
    default: 600
  wait_interval:
    description: Initial polling interval in seconds.
    type: float
    default: 5.0
"""

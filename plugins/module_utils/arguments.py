from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible.module_utils.common.parameters import env_fallback


def connection_argument_spec():
    return dict(
        base_url=dict(type="str", required=True, fallback=(env_fallback, ["OCP_URL"])),
        username=dict(type="str", fallback=(env_fallback, ["OCP_USERNAME"])),
        password=dict(type="str", no_log=True, fallback=(env_fallback, ["OCP_PASSWORD"])),
        access_key=dict(type="str", no_log=True, fallback=(env_fallback, ["OCP_ACCESS_KEY"])),
        secret_key=dict(type="str", no_log=True, fallback=(env_fallback, ["OCP_SECRET_KEY"])),
        validate_certs=dict(type="bool", default=True),
        timeout=dict(type="int", default=30),
        retries=dict(type="int", default=3),
        retry_backoff=dict(type="float", default=1.0),
        accept_language=dict(type="str", default="zh-CN"),
        origin=dict(type="str", default="ansible-oceanbase.ocp"),
        headers=dict(type="dict", default={}),
    )


def logging_argument_spec():
    return dict(
        log_file=dict(type="str"),
        log_level=dict(type="str", choices=["DEBUG", "INFO", "WARNING", "ERROR"], default="INFO"),
        log_request_body=dict(type="bool", default=False),
    )


def wait_argument_spec():
    return dict(
        wait=dict(type="bool", default=True),
        wait_timeout=dict(type="int", default=600),
        wait_interval=dict(type="float", default=5.0),
    )


def combined_argument_spec(*specs):
    result = {}
    for spec in specs:
        result.update(spec)
    return result

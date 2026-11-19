from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.oceanbase.ocp.plugins.module_utils.arguments import (
    combined_argument_spec,
    connection_argument_spec,
    logging_argument_spec,
    wait_argument_spec,
)
from ansible_collections.oceanbase.ocp.plugins.module_utils.client import OCPAPIError, OCPClient
from ansible_collections.oceanbase.ocp.plugins.module_utils.logger import OCPLogger
from ansible_collections.oceanbase.ocp.plugins.module_utils.resources import OCPResourceError
from ansible_collections.oceanbase.ocp.plugins.module_utils.tasks import (
    OCPTaskError,
    extract_task_id,
    wait_for_task,
)


def create_module(extra_spec=None, include_wait=False, **kwargs):
    specs = [connection_argument_spec(), logging_argument_spec()]
    if include_wait:
        specs.append(wait_argument_spec())
    if extra_spec:
        specs.append(extra_spec)
    kwargs.setdefault("required_together", [])
    kwargs["required_together"] = list(kwargs["required_together"]) + [
        ["username", "password"], ["access_key", "secret_key"],
    ]
    kwargs.setdefault("mutually_exclusive", [])
    kwargs["mutually_exclusive"] = list(kwargs["mutually_exclusive"]) + [["username", "access_key"]]
    kwargs.setdefault("required_one_of", [])
    kwargs["required_one_of"] = list(kwargs["required_one_of"]) + [["username", "access_key"]]
    return AnsibleModule(
        argument_spec=combined_argument_spec(*specs), supports_check_mode=True, **kwargs
    )


def create_client(module, name="ocp.module"):
    logger = OCPLogger(
        name, module=module, log_file=module.params.get("log_file"),
        log_level=module.params.get("log_level", "INFO"),
    )
    return OCPClient(module, logger=logger)


def maybe_wait(client, response, wait, timeout, interval):
    if not wait or response is None:
        return None
    task_id = extract_task_id(response)
    if task_id is None:
        return None
    return wait_for_task(client, task_id, timeout=timeout, interval=interval)


def response_result(changed=False, response=None, **values):
    result = {"changed": changed}
    result.update(values)
    if response is not None:
        result.update(response=response.body, status=response.status, trace_id=response.trace_id)
    return result


def run_module(module, handler):
    try:
        result = handler(module, create_client(module, getattr(module, "name", "ocp.module")))
        module.exit_json(**result)
    except OCPAPIError as error:
        module.fail_json(**error.as_dict())
    except OCPTaskError as error:
        module.fail_json(msg=str(error), task=error.task)
    except OCPResourceError as error:
        module.fail_json(msg=str(error))

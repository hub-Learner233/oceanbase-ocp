from ansible_collections.oceanbase.ocp.plugins.module_utils.arguments import (
    connection_argument_spec,
    logging_argument_spec,
    wait_argument_spec,
)


def test_shared_argument_specs_mark_secrets_no_log():
    connection = connection_argument_spec()
    assert connection["password"]["no_log"] is True
    assert connection["secret_key"]["no_log"] is True
    assert connection["validate_certs"]["default"] is True
    assert wait_argument_spec()["wait"]["type"] == "bool"
    assert logging_argument_spec()["log_level"]["default"] == "INFO"

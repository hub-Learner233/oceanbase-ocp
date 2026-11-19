import base64

from ansible_collections.oceanbase.ocp.plugins.module_utils.auth import (
    aksk_auth_headers,
    basic_auth_header,
    build_string_to_sign,
)


def test_basic_auth_header():
    assert basic_auth_header("foo", "bar") == "Basic " + base64.b64encode(b"foo:bar").decode("ascii")


def test_official_aksdk_signature_example():
    params = {
        "startTime": "2024-04-15T14:29:55+08:00",
        "endTime": "2024-04-15T14:30:55+08:00",
        "maxPoints": "360",
        "metrics": "host_disk_total",
        "labels": "svr_ip:127.0.0.1",
        "groupBy": "app,svr_ip,device,mount_point",
    }
    headers = aksk_auth_headers(
        access_key="gDCcIqbkJJINjXBn",
        secret_key="d75332c5eed8d440a84a35ac6248d397",
        method="GET",
        base_url="http://127.0.0.1:8080",
        path="/api/v2/monitor/top",
        query=params,
        headers={"x-ocp-origin": "for-test", "Content-Type": "application/json"},
        body=None,
        request_date="Mon, 15 Apr 2024 09:25:02 GMT",
    )
    assert headers["Authorization"] == (
        "OCP-ACCESS-KEY-HMACSHA1 gDCcIqbkJJINjXBn:To11kg1EsB/dPWyDnnpuUzIUoQk="
    )
    assert headers["Date"] == "Mon, 15 Apr 2024 09:25:02 GMT"


def test_string_to_sign_includes_uppercase_body_md5_and_sorted_query():
    value = build_string_to_sign(
        method="post",
        host="ocp.example:8080",
        path="/api/v2/test",
        query={"z": "last", "a": "hello world"},
        headers={"Content-Type": "application/json", "X-OCP-B": "2", "x-ocp-a": "1"},
        body=b"{}",
        request_date="Tue, 17 Jan 2023 03:36:01 GMT",
    )
    lines = value.split("\n")
    assert lines[0] == "POST"
    assert lines[1] == "99914B932BD37A50B983C5E7C90AE93B"
    assert "a=hello+world&z=last" in lines[-1]
    assert "x-ocp-a:1\nx-ocp-b:2" in value

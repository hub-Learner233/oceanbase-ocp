import io
import json
from urllib.error import HTTPError, URLError

import pytest

from ansible_collections.oceanbase.ocp.plugins.module_utils.client import (
    OCPAPIError,
    OCPClient,
    OCPResponse,
)


class Module(object):
    def __init__(self, **overrides):
        self.params = dict(
            base_url="http://ocp.example:8080",
            username="admin",
            password="secret",
            access_key=None,
            secret_key=None,
            validate_certs=True,
            timeout=10,
            retries=3,
            retry_backoff=0,
            accept_language="zh-CN",
            origin="tests",
            headers={},
            log_request_body=False,
        )
        self.params.update(overrides)


class Reply(object):
    def __init__(self, payload, status=200):
        self.status = status
        self.headers = {"Content-Type": "application/json"}
        self._body = json.dumps(payload).encode("utf-8")

    def read(self):
        return self._body


def test_request_unwraps_successful_ocp_envelope():
    def opener(url, **kwargs):
        assert url == "http://ocp.example:8080/api/v2/ob/clusters?page=1"
        assert kwargs["headers"]["Authorization"].startswith("Basic ")
        return Reply({"successful": True, "status": 200, "traceId": "trace-1", "data": {"contents": []}})

    response = OCPClient(Module(), opener=opener, sleep=lambda _: None).request("GET", "/api/v2/ob/clusters", query={"page": 1})
    assert isinstance(response, OCPResponse)
    assert response.data == {"contents": []}
    assert response.trace_id == "trace-1"


def test_unsuccessful_envelope_raises_error_with_trace_id():
    client = OCPClient(Module(), opener=lambda *a, **k: Reply({"successful": False, "message": "denied", "traceId": "t-2"}), sleep=lambda _: None)
    with pytest.raises(OCPAPIError, match="denied") as error:
        client.request("GET", "/api/v2/info")
    assert error.value.trace_id == "t-2"


def test_post_connection_error_is_not_retried():
    calls = []

    def opener(*args, **kwargs):
        calls.append(args)
        raise URLError("offline")

    client = OCPClient(Module(), opener=opener, sleep=lambda _: None)
    with pytest.raises(OCPAPIError):
        client.request("POST", "/api/v2/ob/clusters", body={"name": "db"})
    assert len(calls) == 1


def test_get_server_error_is_retried():
    calls = []

    def opener(url, **kwargs):
        calls.append(url)
        if len(calls) == 1:
            raise HTTPError(url, 503, "unavailable", {}, io.BytesIO(b"{}"))
        return Reply({"successful": True, "data": {"ok": True}})

    response = OCPClient(Module(), opener=opener, sleep=lambda _: None).request("GET", "/api/v2/info")
    assert response.data == {"ok": True}
    assert len(calls) == 2


def test_list_all_follows_ocp_page_metadata():
    def opener(url, **kwargs):
        page = 2 if "page=2" in url else 1
        payload = {
            "successful": True,
            "data": {
                "contents": [{"id": page}],
                "page": {"number": page, "size": 1, "totalPages": 2, "totalElements": 2},
            },
        }
        return Reply(payload)

    items, page = OCPClient(Module(), opener=opener, sleep=lambda _: None).list_all("/api/v2/ob/clusters", query={"size": 1})
    assert items == [{"id": 1}, {"id": 2}]
    assert page["totalElements"] == 2

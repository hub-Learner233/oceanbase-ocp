from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json
import time
from urllib.error import HTTPError, URLError

from ansible.module_utils.urls import open_url

from ansible_collections.oceanbase.ocp.plugins.module_utils.auth import (
    aksk_auth_headers,
    basic_auth_header,
    canonical_query,
)
from ansible_collections.oceanbase.ocp.plugins.module_utils.logger import OCPLogger

IDEMPOTENT_METHODS = {"GET", "HEAD", "OPTIONS", "PUT", "DELETE"}
RETRYABLE_STATUS = {429, 500, 502, 503, 504}


class OCPAPIError(Exception):
    def __init__(self, message, method=None, path=None, status=None, trace_id=None, response=None):
        self.method = method
        self.path = path
        self.status = status
        self.trace_id = trace_id
        self.response = response
        context = []
        if method:
            context.append(method)
        if path:
            context.append(path)
        if status is not None:
            context.append("HTTP %s" % status)
        if trace_id:
            context.append("traceId=%s" % trace_id)
        super(OCPAPIError, self).__init__("%s (%s)" % (message, ", ".join(context)) if context else message)

    def as_dict(self):
        return dict(
            msg=str(self), method=self.method, path=self.path,
            status=self.status, trace_id=self.trace_id, response=self.response,
        )


class OCPResponse(object):
    def __init__(self, status, headers, body):
        self.status = status
        self.headers = headers
        self.body = body
        self.trace_id = body.get("traceId") if isinstance(body, dict) else None
        if isinstance(body, dict) and ("successful" in body or "traceId" in body):
            self.data = body.get("data")
        else:
            self.data = body


class OCPClient(object):
    def __init__(self, module, logger=None, opener=None, sleep=None):
        self.module = module
        self.params = module.params
        self.base_url = self.params["base_url"].rstrip("/")
        self.logger = logger or OCPLogger(
            "ocp.client", module=module,
            log_file=self.params.get("log_file"), log_level=self.params.get("log_level", "INFO"),
        )
        self.opener = opener or open_url
        self.sleep = sleep or time.sleep

    def _headers(self, method, path, query, headers, body):
        result = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Accept-Language": self.params.get("accept_language") or "zh-CN",
            "x-ocp-origin": self.params.get("origin") or "ansible-oceanbase.ocp",
        }
        result.update(self.params.get("headers") or {})
        result.update(headers or {})
        if self.params.get("access_key") or self.params.get("secret_key"):
            result.update(aksk_auth_headers(
                self.params["access_key"], self.params["secret_key"], method,
                self.base_url, path, query, result, body,
            ))
        else:
            result["Authorization"] = basic_auth_header(
                self.params.get("username") or "", self.params.get("password") or "",
            )
        return result

    @staticmethod
    def _decode(raw):
        if raw is None or raw == b"" or raw == "":
            return None
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8", errors="replace")
        try:
            return json.loads(raw)
        except (TypeError, ValueError) as error:
            raise OCPAPIError("OCP returned invalid JSON: %s" % error, response=raw[:2000])

    def _validate(self, method, path, response):
        body = response.body
        if isinstance(body, dict) and body.get("successful") is False:
            message = body.get("message") or body.get("error") or body.get("errMsg") or "OCP rejected the request"
            raise OCPAPIError(message, method, path, response.status, response.trace_id, body)
        if not 200 <= response.status < 300:
            message = "OCP request failed"
            if isinstance(body, dict):
                message = body.get("message") or body.get("error") or message
            raise OCPAPIError(message, method, path, response.status, response.trace_id, body)
        return response

    def request(self, method, path, query=None, body=None, headers=None):
        method = method.upper()
        if not path.startswith("/"):
            path = "/" + path
        query = query or {}
        payload = None if body is None else (
            body if isinstance(body, bytes) else json.dumps(body, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        )
        query_string = canonical_query(query)
        url = self.base_url + path + ("?" + query_string if query_string else "")
        retries = max(0, int(self.params.get("retries", 3)))
        backoff = max(0.0, float(self.params.get("retry_backoff", 1.0)))
        can_retry = method in IDEMPOTENT_METHODS
        last_error = None

        for attempt in range(retries + 1):
            request_headers = self._headers(method, path, query, headers, payload)
            self.logger.debug(
                "OCP request", method=method, path=path, query=query,
                body=body if self.params.get("log_request_body") else None, attempt=attempt + 1,
            )
            try:
                raw_response = self.opener(
                    url, data=payload, headers=request_headers, method=method,
                    timeout=self.params.get("timeout", 30),
                    validate_certs=self.params.get("validate_certs", True),
                    follow_redirects="safe",
                )
                status = getattr(raw_response, "status", None) or raw_response.getcode()
                response_headers = dict(getattr(raw_response, "headers", {}) or {})
                response = OCPResponse(status, response_headers, self._decode(raw_response.read()))
                if hasattr(raw_response, "close"):
                    raw_response.close()
                response = self._validate(method, path, response)
                self.logger.debug("OCP response", method=method, path=path, status=status, trace_id=response.trace_id)
                return response
            except HTTPError as error:
                raw = error.read()
                try:
                    decoded = self._decode(raw)
                except OCPAPIError:
                    decoded = raw.decode("utf-8", errors="replace")[:2000]
                trace_id = decoded.get("traceId") if isinstance(decoded, dict) else None
                last_error = OCPAPIError(
                    (decoded.get("message") or decoded.get("error")) if isinstance(decoded, dict) else error.reason,
                    method, path, error.code, trace_id, decoded,
                )
                if not can_retry or error.code not in RETRYABLE_STATUS or attempt >= retries:
                    raise last_error
            except URLError as error:
                last_error = OCPAPIError("Cannot connect to OCP: %s" % error.reason, method, path)
                if not can_retry or attempt >= retries:
                    raise last_error
            except OCPAPIError:
                raise
            if attempt < retries:
                self.sleep(backoff * (2 ** attempt))
        raise last_error

    def get_data(self, path, query=None):
        return self.request("GET", path, query=query).data

    def list_all(self, path, query=None):
        query = dict(query or {})
        page_number = int(query.pop("page", 1))
        size = int(query.get("size", 200))
        resources = []
        page = {}
        while True:
            request_query = dict(query, page=page_number)
            data = self.get_data(path, query=request_query)
            if isinstance(data, list):
                resources.extend(data)
                page = {"number": page_number, "size": size, "totalElements": len(resources), "totalPages": 1}
                break
            if not isinstance(data, dict):
                raise OCPAPIError("Expected a paged OCP object", "GET", path, response=data)
            contents = data.get("contents", [])
            resources.extend(contents)
            page = data.get("page") or {}
            total_pages = page.get("totalPages", page.get("totalPage"))
            if total_pages is None:
                total_pages = page_number if len(contents) < size else page_number + 1
            if page_number >= int(total_pages) or not contents:
                break
            page_number += 1
        return resources, page

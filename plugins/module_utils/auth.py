from __future__ import absolute_import, division, print_function

__metaclass__ = type

import base64
import hashlib
import hmac
from email.utils import formatdate
from urllib.parse import quote_plus, urlsplit


def basic_auth_header(username, password):
    credentials = ("%s:%s" % (username, password)).encode("utf-8")
    return "Basic " + base64.b64encode(credentials).decode("ascii")


def _query_pairs(query):
    if not query:
        return []
    pairs = []
    for key, value in query.items():
        values = value if isinstance(value, (list, tuple)) else [value]
        for item in values:
            if isinstance(item, bool):
                item = str(item).lower()
            elif item is None:
                item = ""
            else:
                item = str(item)
            pairs.append((str(key), item))
    return sorted(pairs, key=lambda pair: (pair[0], pair[1]))


def canonical_query(query):
    return "&".join(
        "%s=%s" % (quote_plus(key, encoding="utf-8"), quote_plus(value, encoding="utf-8"))
        for key, value in _query_pairs(query)
    )


def _header_value(headers, name):
    for key, value in headers.items():
        if key.lower() == name.lower():
            return str(value)
    return ""


def build_string_to_sign(method, host, path, query, headers, body, request_date):
    payload_md5 = hashlib.md5(body).hexdigest().upper() if body is not None else ""
    ocp_headers = sorted(
        (str(key).lower(), str(value)) for key, value in headers.items() if str(key).lower().startswith("x-ocp-")
    )
    ocp_header_text = "\n".join("%s:%s" % (key, value) for key, value in ocp_headers)
    canonical_path = path
    query_string = canonical_query(query)
    if query_string:
        canonical_path += "?" + query_string
    return "\n".join([
        method.upper(),
        payload_md5,
        _header_value(headers, "Content-Type"),
        request_date,
        host,
        ocp_header_text,
        canonical_path,
    ])


def aksk_auth_headers(access_key, secret_key, method, base_url, path, query, headers, body, request_date=None):
    request_date = request_date or formatdate(usegmt=True)
    host = urlsplit(base_url).netloc
    string_to_sign = build_string_to_sign(method, host, path, query, headers, body, request_date)
    digest = hmac.new(secret_key.encode("utf-8"), string_to_sign.encode("utf-8"), hashlib.sha1).digest()
    signature = base64.b64encode(digest).decode("ascii")
    return {
        "Authorization": "OCP-ACCESS-KEY-HMACSHA1 %s:%s" % (access_key, signature),
        "Date": request_date,
    }

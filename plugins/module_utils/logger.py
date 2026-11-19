from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json
import os
import threading
from datetime import datetime, timezone

SENSITIVE_KEYS = {
    "authorization", "password", "passwd", "secret", "secret_key", "secretkey",
    "accesskeysecret", "rootpassword", "newpassword", "token", "private_key",
}
_LEVELS = {"DEBUG": 10, "INFO": 20, "WARNING": 30, "ERROR": 40}
_LOCK = threading.Lock()


def _sensitive(key):
    normalized = str(key).replace("_", "").replace("-", "").lower()
    return normalized in {item.replace("_", "") for item in SENSITIVE_KEYS}


def redact(value, key=None):
    if key is not None and _sensitive(key):
        return "***"
    if isinstance(value, dict):
        return {item_key: redact(item_value, item_key) for item_key, item_value in value.items()}
    if isinstance(value, list):
        return [redact(item) for item in value]
    if isinstance(value, tuple):
        return tuple(redact(item) for item in value)
    return value


class OCPLogger(object):
    def __init__(self, name, module=None, log_file=None, log_level="INFO"):
        self.name = name
        self.module = module
        self.log_file = log_file
        self.threshold = _LEVELS[log_level.upper()]

    def _write(self, level, message, fields):
        if _LEVELS[level] < self.threshold:
            return
        safe_fields = redact(fields)
        if self.module is not None:
            text = "%s %s" % (message, json.dumps(safe_fields, ensure_ascii=False, default=str))
            if level == "DEBUG" and hasattr(self.module, "debug"):
                self.module.debug(text)
            elif hasattr(self.module, "log"):
                self.module.log("[oceanbase.ocp] " + text)
        if self.log_file:
            record = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "logger": self.name,
                "level": level,
                "message": message,
                "fields": safe_fields,
            }
            directory = os.path.dirname(os.path.abspath(self.log_file))
            os.makedirs(directory, exist_ok=True)
            with _LOCK:
                with open(self.log_file, "a", encoding="utf-8") as stream:
                    stream.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")

    def debug(self, message, **fields):
        self._write("DEBUG", message, fields)

    def info(self, message, **fields):
        self._write("INFO", message, fields)

    def warning(self, message, **fields):
        self._write("WARNING", message, fields)

    def error(self, message, **fields):
        self._write("ERROR", message, fields)

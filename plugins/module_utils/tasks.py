from __future__ import absolute_import, division, print_function

__metaclass__ = type

import time

SUCCESS_STATES = {"SUCCESSFUL", "SUCCESS", "COMPLETED"}
FAILURE_STATES = {"FAILED", "FAIL", "CANCELED", "CANCELLED", "TIMEOUT"}


class OCPTaskError(Exception):
    def __init__(self, message, task=None):
        self.task = task
        super(OCPTaskError, self).__init__(message)


def extract_task_id(response):
    if hasattr(response, "body"):
        response = response.body
    if not isinstance(response, dict):
        return None
    data = response.get("data", response)
    if isinstance(data, dict) and "contents" not in data and data.get("id") is not None and data.get("status"):
        return data["id"]
    return None


def wait_for_task(client, task_id, timeout=600, interval=5, sleep=None, monotonic=None):
    sleep = sleep or time.sleep
    monotonic = monotonic or time.monotonic
    started = monotonic()
    while True:
        task = client.get_data("/api/v2/tasks/instances/%s" % task_id)
        if not isinstance(task, dict):
            raise OCPTaskError("OCP task %s returned an invalid object" % task_id, task)
        status = str(task.get("status", "")).upper()
        if status in SUCCESS_STATES:
            return task
        if status in FAILURE_STATES:
            raise OCPTaskError("OCP task %s ended with status %s" % (task_id, status), task)
        if monotonic() - started >= timeout:
            raise OCPTaskError("OCP task %s timed out after %s seconds" % (task_id, timeout), task)
        sleep(interval)

# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
name: ocp_log
short_description: Write structured JSON Lines audit logs for OCP playbooks
version_added: 0.1.0
author:
  - OceanBase OCP Collection contributors (!UNKNOWN)
type: aggregate
description:
  - Writes play, task result and playbook statistics events to a local JSON Lines file.
  - This is a controller-side callback and complements module-side request logging.
requirements:
  - Add C(callbacks_enabled=oceanbase.ocp.ocp_log) to ansible.cfg.
options:
  log_file:
    description: Controller-side JSON Lines destination.
    type: str
    env: [{name: OCP_CALLBACK_LOG_FILE}]
    ini: [{section: callback_ocp_log, key: log_file}]
    required: true
  log_level:
    description: Minimum event severity to write.
    type: str
    choices: [DEBUG, INFO, WARNING, ERROR]
    default: INFO
    env: [{name: OCP_CALLBACK_LOG_LEVEL}]
    ini: [{section: callback_ocp_log, key: log_level}]
"""

import json
import os
import threading
from datetime import datetime, timezone

from ansible.plugins.callback import CallbackBase

from ansible_collections.oceanbase.ocp.plugins.module_utils.logger import redact

LEVELS = {"DEBUG": 10, "INFO": 20, "WARNING": 30, "ERROR": 40}
LOCK = threading.Lock()


class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = "aggregate"
    CALLBACK_NAME = "oceanbase.ocp.ocp_log"
    CALLBACK_NEEDS_ENABLED = True

    def __init__(self, display=None):
        super(CallbackModule, self).__init__(display=display)
        self.play = None

    def _write(self, event, level="INFO", **fields):
        log_level = self._plugin_options.get("log_level", "INFO")
        if LEVELS[level] < LEVELS[log_level]:
            return
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event,
            "level": level,
            "play": self.play,
        }
        record.update(redact(fields))
        path = self._plugin_options.get("log_file")
        if not path:
            return
        directory = os.path.dirname(os.path.abspath(path))
        os.makedirs(directory, exist_ok=True)
        with LOCK:
            with open(path, "a", encoding="utf-8") as stream:
                stream.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")

    def v2_playbook_on_play_start(self, play):
        self.play = play.get_name()
        self._write("play_start", play=play.get_name(), hosts=play.hosts)

    def _result(self, result, status, level="INFO"):
        self._write(
            "task_result", level=level, host=result._host.name,
            task=result._task.action, task_path=result._task.get_path(),
            status=status, result=result._result,
        )

    def v2_runner_on_ok(self, result):
        self._result(result, "ok")

    def v2_runner_on_failed(self, result, ignore_errors=False):
        self._result(result, "failed", "ERROR")

    def v2_runner_on_skipped(self, result):
        self._result(result, "skipped", "DEBUG")

    def v2_playbook_on_stats(self, stats):
        hosts = sorted(stats.processed)
        self._write("playbook_stats", stats={host: stats.summarize(host) for host in hosts})

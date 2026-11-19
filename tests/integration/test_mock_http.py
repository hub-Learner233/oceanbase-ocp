import json
import os
from pathlib import Path
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from ansible_collections.oceanbase.ocp.plugins.module_utils.client import OCPClient
from ansible_collections.oceanbase.ocp.plugins.module_utils.tasks import wait_for_task


class Handler(BaseHTTPRequestHandler):
    requests = []

    def _send(self, payload, status=200):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        type(self).requests.append(("GET", self.path, self.headers.get("Authorization")))
        if self.path == "/api/v2/info":
            self._send({"name": "ocp-server", "buildVersion": "test"})
        elif self.path == "/api/v2/tasks/instances/7":
            self._send({"successful": True, "data": {"id": 7, "status": "SUCCESSFUL"}})
        else:
            self._send({"successful": False, "message": "not found", "traceId": "mock-404"}, 404)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        payload = json.loads(self.rfile.read(length))
        type(self).requests.append(("POST", self.path, payload))
        self._send({"successful": True, "data": {"id": 7, "status": "RUNNING"}})

    def log_message(self, format, *args):
        pass


def test_real_ansible_http_transport_and_async_task():
    Handler.requests = []
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        module = type("Module", (), {"params": {
            "base_url": "http://127.0.0.1:%s" % server.server_port,
            "username": "admin", "password": "secret", "access_key": None, "secret_key": None,
            "validate_certs": True, "timeout": 5, "retries": 0, "retry_backoff": 0,
            "accept_language": "zh-CN", "origin": "pytest", "headers": {},
            "log_file": None, "log_level": "ERROR", "log_request_body": False,
        }})()
        client = OCPClient(module)
        assert client.get_data("/api/v2/info")["buildVersion"] == "test"
        response = client.request("POST", "/api/v2/ob/clusters", body={"name": "test"})
        task = wait_for_task(client, response.data["id"], timeout=1, interval=0)
        assert task["status"] == "SUCCESSFUL"
        assert Handler.requests[0][2].startswith("Basic ")
        assert Handler.requests[1] == ("POST", "/api/v2/ob/clusters", {"name": "test"})
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_real_ansible_module_execution(tmp_path):
    Handler.requests = []
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    collection_parent = tmp_path / "ansible_collections" / "oceanbase"
    collection_parent.mkdir(parents=True)
    (collection_parent / "ocp").symlink_to(Path(__file__).resolve().parents[2], target_is_directory=True)
    env = os.environ.copy()
    env["ANSIBLE_COLLECTIONS_PATH"] = str(tmp_path)
    env["ANSIBLE_LOCALHOST_WARNING"] = "False"
    env["ANSIBLE_INVENTORY_UNPARSED_WARNING"] = "False"
    command = [
        str(Path(sys.executable).with_name("ansible")), "localhost", "-i", "localhost,",
        "-c", "local", "-m", "oceanbase.ocp.ocp_info", "-a",
        "base_url=http://127.0.0.1:%s username=admin password=secret" % server.server_port,
    ]
    try:
        result = subprocess.run(command, env=env, capture_output=True, text=True, timeout=30, check=False)
        assert result.returncode == 0, result.stdout + result.stderr
        assert '"buildVersion": "test"' in result.stdout
        assert Handler.requests == [("GET", "/api/v2/info", Handler.requests[0][2])]
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

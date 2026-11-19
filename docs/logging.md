# 日志与审计

## 模块侧日志

所有模块支持：

- `log_file`：模块执行主机上的 JSON Lines 文件。
- `log_level`：DEBUG、INFO、WARNING、ERROR。
- `log_request_body`：默认 false；启用后也只写递归脱敏后的请求体。

每条记录包含 UTC 时间、logger、级别、消息和 fields。HTTP 日志包含方法、路径、状态、重试次数和 traceId，不记录 Authorization 或 SK。响应体默认不写入文件。

## 控制端回调

在 `ansible.cfg` 中启用：

```ini
[defaults]
callbacks_enabled = oceanbase.ocp.ocp_log

[callback_ocp_log]
log_file = ./logs/ocp-playbook.jsonl
log_level = INFO
```

也可使用环境变量 `OCP_CALLBACK_LOG_FILE` 和 `OCP_CALLBACK_LOG_LEVEL`。回调记录 play 开始、task 成功/失败/跳过及最终统计。Ansible 已将 `no_log` 参数替换为占位符，回调还会再次按键名脱敏。

## 权限与轮转

日志文件可能包含集群名、主机 IP 和运维结果，应按敏感运维数据设置文件权限并配置 logrotate。Collection 不主动轮转日志，避免与系统日志策略冲突。

```logrotate
/var/log/ansible/ocp-*.jsonl {
    daily
    rotate 14
    compress
    missingok
    notifempty
    create 0640 root adm
}
```

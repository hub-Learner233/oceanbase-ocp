# OCP REST API 使用指南

## 统一约定

OCP Open API 使用 JSON 请求体，常见方法为 GET、PUT、POST、DELETE。常见列表响应为：

```json
{
  "data": {
    "contents": [],
    "page": {"number": 1, "size": 10, "totalElements": 0, "totalPages": 1}
  },
  "successful": true,
  "status": 200,
  "traceId": "..."
}
```

客户端保留完整 `response`，同时将 `data` 解包返回。请求失败时保留 HTTP 状态、路径和 `traceId`。

## 常用官方路径

| 功能 | 方法与路径 |
|---|---|
| OCP 信息 | `GET /api/v2/info` |
| 集群列表 | `GET /api/v2/ob/clusters` |
| 创建集群 | `POST /api/v2/ob/clusters` |
| 删除集群 | `DELETE /api/v2/ob/clusters/{id}` |
| 集群启停重启 | `POST /api/v2/ob/clusters/{id}/{start|stop|restart}` |
| OBServer 列表 | `GET /api/v2/ob/clusters/{id}/servers` |
| 租户列表/创建 | `GET|POST /api/v2/ob/clusters/{id}/tenants` |
| 删除租户 | `DELETE /api/v2/ob/clusters/{id}/tenants/{tenantId}` |
| 主机列表 | `GET /api/v2/compute/hosts` |
| OBProxy 集群 | `GET /api/v2/obproxy/clusters` |
| 任务列表/详情 | `GET /api/v2/tasks/instances[/{taskId}]` |
| 巡检任务 | `GET /api/v2/inspection/task` |
| 推送告警 | `POST /api/v2/alarm/alarms` |

其他功能直接通过 `ocp_api` 使用官方路径，无需等待 Collection 增加新模块。

## 异步任务

创建集群、创建租户和集群启停等操作通常返回任务对象。专用变更模块默认 `wait: true`，提取 `data.id` 后轮询任务详情。通用 `ocp_api` 默认 `wait: false`，避免把普通资源误识别为任务；异步接口应显式启用。

终态成功：`SUCCESSFUL`、`SUCCESS`、`COMPLETED`。失败或取消会使 Ansible 任务失败并返回最后的任务对象。轮询超时由 `wait_timeout` 控制。

## 分页与查询数组

专用 info 模块默认自动遍历全部页。`query` 字典中列表值会编码为重复 query 参数；如果某个 OCP 版本要求逗号分隔，请直接传字符串，例如 `status: "RUNNING,STOPPED"`。

## 变更语义

`ocp_api` 默认 GET/HEAD/OPTIONS 返回 `changed=false`，其他方法返回 `changed=true`，可用 `changed` 参数覆盖。check mode 下安全方法仍执行，变更方法只返回计划请求且不发送 body。

专用资源模块以名称做精确幂等匹配；同名多个资源会报错，避免任意选择。复杂更新不属于隐式 `present` 行为，应使用官方更新接口。

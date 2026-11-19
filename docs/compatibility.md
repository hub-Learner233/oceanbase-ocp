# 兼容性与官方参考

## 支持范围

- `ansible-core >= 2.15`。
- Python 3.9 及以上，具体解释器支持范围同时受 ansible-core 版本约束。
- OCP `/api/v2` Open API；以目标 OCP 版本的接口文档为准。
- 无 `requests` 等运行期依赖，适合 Ansible Execution Environment。

OCP 各版本可能增加或调整创建、备份、容灾、监控和诊断字段。本 Collection 的 `definition`、`body`、`query` 和 `parameters` 均保留官方原生结构，不强制转换成另一套命名。

## 官方资料

- API 调用说明（Basic、AK/SK、JSON、路径）：https://www.oceanbase.com/docs/common-ocp-1000000003339390
- AK/SK 签名生成规则：https://www.oceanbase.com/docs/common-ocp-1000000000826902
- 创建集群：https://www.oceanbase.com/docs/common-ocp-1000000001406588
- 创建租户：https://www.oceanbase.com/docs/common-ocp-1000000007051638
- 删除租户：https://www.oceanbase.com/docs/common-ocp-1000000006011059
- 查询主机：https://www.oceanbase.com/docs/common-ocp-1000000007051663
- 查询任务：https://www.oceanbase.com/docs/common-ocp-1000000007051608
- 巡检任务：https://www.oceanbase.com/docs/common-ocp-1000000001278089

## 验证边界

仓库测试使用官方签名样例和模拟 HTTP 响应，不连接用户生产环境。部署前应在与目标版本一致的测试 OCP 上验证：认证、权限、分页数组编码、资源 definition、异步任务状态和高风险操作。

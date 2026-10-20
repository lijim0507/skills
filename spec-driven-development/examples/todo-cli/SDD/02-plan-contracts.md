# 02-plan-contracts.md —— Phase 1 模块清单与内部契约

## 模块清单

| 模块 | 一句话职责 | 拥有写权限的数据 |
| --- | --- | --- |
| CommandParser | 解析命令 | 无 |
| TaskStore | 读写待办 | todos.json |
| TaskRenderer | 格式化输出 | 无 |

## 依赖方向

- 允许：CommandParser → TaskStore；TaskRenderer → TaskStore
- 禁止：TaskStore → CommandParser

## 模块间契约

### CommandParser → TaskStore

| 项 | 内容 |
| --- | --- |
| 接口 / 消息 / 事件 | add(text) / list() |
| 输入 | 命令参数 |
| 输出 | 待办对象 / 列表 |
| 错误 | 参数错误 |
| 调用上下文 | 同步 |
| 前置条件 | 数据文件可读 |
| 兼容性 / 版本 | v1 |
| 契约测试 | pytest tests/test_store.py |

### TaskRenderer → TaskStore

| 项 | 内容 |
| --- | --- |
| 接口 / 消息 / 事件 | list() |
| 输入 | 无 |
| 输出 | 待办列表 |
| 错误 | 数据文件损坏 |
| 调用上下文 | 同步 |
| 前置条件 | 无 |
| 兼容性 / 版本 | v1 |
| 契约测试 | pytest tests/test_renderer.py |

## 错误码

| 码 | 含义 | 处置 |
| --- | --- | --- |
| E001 | 数据文件损坏 | 报错并保留原文件 |

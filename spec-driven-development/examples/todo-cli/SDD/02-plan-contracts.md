# 02-plan-contracts.md —— Phase 1 模块清单与公开接口

## 模块清单

| 模块 | 一句话职责 | 拥有写权限的数据 |
| --- | --- | --- |
| CommandParser | 解析命令并分发 | 无 |
| TaskStore | 读写待办 | todos.json |
| TaskRenderer | 格式化输出 | 无 |

## 依赖方向

- 允许：CommandParser → TaskStore；TaskRenderer → TaskStore
- 禁止：TaskStore → CommandParser；TaskStore → TaskRenderer

## 模块公开接口

### CommandParser

**公开类型**

| 类型 | 定义 / 来源 | 语义 |
| --- | --- | --- |
| `Command` | `{ const char *action; const char *text; }` | 一条已解析的命令 |

**公开接口**

| 接口 | 输入 | 输出 / 返回 | 错误 | 调用上下文 |
| --- | --- | --- | --- | --- |
| `int command_parse(int argc, char **argv, Command *out)` | 命令行参数 | 0 成功 | -1 参数错误 | 同步 |
| `int command_execute(const Command *cmd)` | 已解析命令 | 0 成功 | -1 未知命令；E001 数据文件损坏 | 同步；内部调用 TaskStore |

**事件与回调**

无。

**模块约束**

- 只做解析与分发，不直接读写 `todos.json`。
- `Command.text` 指向 argv 中的字符串，生命周期不超过本次调用。
- 契约测试：`tests/test_parser.py`

### TaskStore

**公开类型**

| 类型 | 定义 / 来源 | 语义 |
| --- | --- | --- |
| `Todo` | `{ int id; char text[128]; int done; }` | 一条待办 |

**公开接口**

| 接口 | 输入 | 输出 / 返回 | 错误 | 调用上下文 |
| --- | --- | --- | --- | --- |
| `int task_add(const char *text)` | 待办文本 | 0 成功 | -1 参数错误；E001 数据文件损坏 | 同步 |
| `int task_list(Todo *out, size_t cap, size_t *count)` | 输出缓冲、容量 | 0 成功；count 为条数 | -1 参数错误；E001 数据文件损坏 | 同步 |

**事件与回调**

无。

**模块约束**

- 是 `todos.json` 的唯一写者。
- 返回的 `Todo` 是拷贝，调用方不持有文件句柄。
- 契约测试：`tests/test_store.py`

### TaskRenderer

**公开类型**

无。

**公开接口**

| 接口 | 输入 | 输出 / 返回 | 错误 | 调用上下文 |
| --- | --- | --- | --- | --- |
| `void task_render(const Todo *items, size_t count)` | 待办数组、条数 | 无 | 无 | 同步；只读数组 |

**事件与回调**

无。

**模块约束**

- 只读 `Todo` 数组，不读写存储。
- 输出格式由本模块决定，调用方不解析文本。
- 契约测试：`tests/test_renderer.py`

## 错误码

| 码 | 含义 | 处置 |
| --- | --- | --- |
| E001 | 数据文件损坏 | 报错并保留原文件 |
| E002 | 参数错误 | 打印用法，命令不执行 |

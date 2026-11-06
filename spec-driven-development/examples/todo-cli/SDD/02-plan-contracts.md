# 02-plan-contracts.md —— Phase 1 模块清单与公开接口

> 角色：技术总监 ｜ 依据：02-plan.md ｜ 版本：r1 ｜ 状态：已确认

## 模块清单

| 模块 | 一句话职责 | 拥有写权限的数据 |
| --- | --- | --- |
| CommandParser | 解析命令并分发 | 无 |
| TaskStore | 读写待办 | todos.json |
| TaskRenderer | 格式化输出 | 无 |

## 依赖方向

- 允许：CommandParser → TaskStore；CommandParser → TaskRenderer；TaskRenderer → TaskStore
- 禁止：TaskStore → CommandParser；TaskStore → TaskRenderer；TaskRenderer → CommandParser

## 模块公开接口

### CommandParser

**公开类型**

| 类型 | 定义 / 来源 | 语义 |
| --- | --- | --- |
| `Command` | `@dataclass Command(action: str, text: str)` | 一条已解析的命令 |

**公开接口**

| 接口 | 输入 | 输出 / 返回 | 错误 | 调用上下文 |
| --- | --- | --- | --- | --- |
| `parse_args(argv: list[str]) -> Command` | 命令行参数 | Command | E002 参数错误 | 同步 |
| `execute(cmd: Command) -> int` | 已解析命令 | 0 成功 | E001 数据文件损坏；E002 参数错误 | 同步 |

**模块约束**

- 只做解析与分发，不直接读写 `todos.json`。
- `Command.text` 是普通字符串，不设固定长度上限。
- 契约测试：`tests/test_parser.py`

### TaskStore

**公开类型**

| 类型 | 定义 / 来源 | 语义 |
| --- | --- | --- |
| `Todo` | `@dataclass Todo(id: int, text: str, created_at: str)` | 一条待办 |

**公开接口**

| 接口 | 输入 | 输出 / 返回 | 错误 | 调用上下文 |
| --- | --- | --- | --- | --- |
| `add(text: str) -> int` | 待办文本 | 0 成功 | E001 数据文件损坏；E002 参数错误 | 同步 |
| `list_todos() -> list[Todo]` | 无 | 待办列表 | E001 数据文件损坏 | 同步 |

**模块约束**

- 是 `todos.json` 的唯一写者。
- 写入使用临时文件 + 原子替换；失败保留原文件。
- 返回的 `Todo` 是拷贝，调用方不持有文件句柄。
- 契约测试：`tests/test_store.py`

### TaskRenderer

**公开类型**

无。

**公开接口**

| 接口 | 输入 | 输出 / 返回 | 错误 | 调用上下文 |
| --- | --- | --- | --- | --- |
| `render(items: list[Todo]) -> None` | 待办列表 | 无 | 无 | 同步；只读列表 |

**模块约束**

- 只读 `Todo` 列表，不读写存储。
- 输出格式由本模块决定，调用方不解析文本。
- 契约测试：`tests/test_renderer.py`

## 错误码

| 码 | 含义 | 处置 |
| --- | --- | --- |
| E001 | 数据文件损坏 | 报错并保留原文件 |
| E002 | 参数错误 | 打印用法，命令不执行 |

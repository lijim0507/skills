# 04-implementation.md —— Todo CLI 执行记录

> 角色：实现者 ｜ 依据：`03-design-<组件>.md`（每个 02 组件一份：TaskFile / TaskStore / CommandParser / TaskRenderer）｜ 版本：v1.0 ｜ 状态：已验收
> 本文件由**实现者**写：把详细设计执行成代码，按任务拆解、执行、验证、留证据。
> 粒度判据：**一个不知道来龙去脉的执行者，只看这一条任务卡，能做完并自己判定做完没做完。**
> 拆解主线：**先按 02 的架构自底向上搭骨架（5.3.6 驱动层 → 5.3.5 中间层 → 5.3.4 应用层），再按 03 的详细设计逐单元填实现**；三层都要有搭建任务，每层骨架通过后接该层的填充任务。
> 索引行用于扫描和脚本检查；非平凡任务必须有任务卡。

**修订记录/Revision record**

| 版本 | 状态 | 变更内容 | 变更日期 | 更改人 | 批准人 |
| ---- | ---- | -------- | -------- | ------ | ------ |
| v1.0 | 已验收 | 依据四份 `03-design-<组件>.md` 建档并执行 | 2026-11-19 | 示例实现者 | 示例用户 |

## 执行说明

- 执行者 / 验收人：示例实现者 / 示例用户。
- 代码范围 / 分支 / 目录：只改 `src/`、`tests/`、`README.md`；不改 `SDD/` 下的 01 / 02 / 03 正文。
- 通用完成标准（DoD）：`python -m pytest tests/ -q` 全绿；`python -m compileall src` 通过；对外接口与 02 一致；无新增第三方依赖。
- 验证命令 / 环境：Python 3.x 标准库；`TODO_FILE` 指向临时文件，测试间互不污染。
- 汇报格式：回传 pytest 输出摘要 + 关键命令实跑记录，注明对应软件需求 ID 与 ASIL（本例均不适用）。
- 阻塞时找谁：需求缺口找 01，组件 / 接口缺口找 02，软件单元设计缺口找 03，不自己猜。
- 任务拆解（两段式，自底向上，三层均覆盖）：
  1. **搭建**：按 02 的组件定义顺序自底向上（5.3.6 TaskFile → 5.3.5 TaskStore → 5.3.4 CommandParser / TaskRenderer）逐组件立骨架：代码文件、D-001 / D-002 数据定义、IF-INT-004 / 005 接口、初始化；骨架通过静态检查即算搭完。
  2. **填充**：每层骨架通过后，同样自底向上按 `03-design-<组件>.md` 的 8.2 软件单元逐个实现函数（对照 8.2.2 函数设计、7.2.3 函数关系、7.2.4 源代码文件清单）；一个单元一个填充任务。
  - 任务号从 T001 起连续递增、不跳号；同一时刻只做一个任务。
- 覆盖方式：全部任务的「覆盖需求」并集覆盖 01 的 3.1.1 清单（SSR001、SSR002）；「验收判据」从 01 的 3.3 需求卡摘录验证准则与验证方法。

## 执行批次

| 批次 | 进入条件 | 可并行 |
| ---- | -------- | ------ |
| B1   | 环境就绪（Python 3 可用、`tests/` 空目录可建） | 是 |
| B2   | B1 全部完成（三层骨架通过 compileall） | 否 |

## 任务

- [x] T001 [B1] 搭建 5.3.6.1 TaskFile 骨架 | SSR001, SSR002
- [x] T002 [B1] 搭建 5.3.5.1 TaskStore 骨架 | SSR001, SSR002
- [x] T003 [B1] 搭建 5.3.4.1 CommandParser 骨架 | SSR001, SSR002
- [x] T004 [B1] 搭建 5.3.4.2 TaskRenderer 骨架 | SSR002
- [x] T005 [B2] 填充 5.3.6.1 TaskFile / 8.2 task_file | SSR001, SSR002
- [x] T006 [B2] 填充 5.3.5.1 TaskStore / 8.2 store | SSR001, SSR002
- [x] T007 [B2] 填充 5.3.4.1 CommandParser / 8.2 parser | SSR001, SSR002
- [x] T008 [B2] 填充 5.3.4.2 TaskRenderer / 8.2 renderer | SSR002

状态：`[ ]` 未完成 ｜ `[x]` 已完成 ｜ `[~]` 已作废

## 任务卡

### T001 搭建 5.3.6.1 TaskFile 骨架

| 字段 | 内容 |
| --- | --- |
| 归属 | 02 组件 5.3.6.1 TaskFile |
| 类型 | 搭建 |
| 批次 | B1 |
| 执行者 | 示例实现者 |
| 验收人 | 示例用户 |
| 目标 | 建立 `src/task_file.py` 骨架：`read` / `write` 两个空实现、StoreError 异常类、D-001 文件结构注释 |
| 范围 | 只建 `src/task_file.py` 与 `src/errors.py`；不写解析逻辑，不碰 TaskStore |
| 输入 | 02 的 5.3.6.1 组件定义、5.3.1 D-001、5.3.2 IF-INT-004 / IF-INT-005；03 的 7.2.4 源代码文件清单 |
| 产出 | 骨架代码、`python -m compileall src` 通过 |
| 完成判据（DoD） | 两个函数可被导入；异常类型与 02 的 5.7 EX-003 对应；无业务逻辑 |
| 覆盖需求 | SSR001、SSR002 |
| 验收判据 | 无独立验收（骨架任务，验收在 T005） |
| 验证 | `python -c "import sys; sys.path.insert(0,'src'); import task_file"` 应无输出无异常 |
| 证据 | T005 的 pytest 输出涵盖本任务接口；compileall 输出见 `tests/logs/compileall.log` |
| 依赖 | 无 |
| 可并行 | 是 |
| 规模 | S |
| 风险 / 回滚 | 骨架若提前写入业务规则会与 03 冲突；回滚即删除文件重来 |

### T002 搭建 5.3.5.1 TaskStore 骨架

| 字段 | 内容 |
| --- | --- |
| 归属 | 02 组件 5.3.5.1 TaskStore |
| 类型 | 搭建 |
| 批次 | B1 |
| 执行者 | 示例实现者 |
| 验收人 | 示例用户 |
| 目标 | 建立 `src/store.py` 骨架：类与 `add` / `list` / `load` / `save` 四个空方法，构造时读 `TODO_FILE` |
| 范围 | 只建 `src/store.py`；不实现校验与持久化细节 |
| 输入 | 02 的 5.3.5.1 组件定义、5.3.1 D-002、5.3.2 IF-INT-002 / 003；03 的 7.2.4 |
| 产出 | 骨架代码、compileall 通过 |
| 完成判据（DoD） | 四个方法签名与 02 的接口表一致；内部属性 `todos` / `path` 存在且初值正确 |
| 覆盖需求 | SSR001、SSR002 |
| 验收判据 | 无独立验收（验收在 T006） |
| 验证 | `python -c "import store; s=store.TaskStore('x.json'); assert s.todos==[]"` |
| 证据 | T006 的 pytest 输出涵盖本任务接口 |
| 依赖 | T001 |
| 可并行 | 否 |
| 规模 | S |
| 风险 / 回滚 | 骨架期直接调用 TaskFile 会因为它是空实现而失败，属预期；回滚删文件重来 |

### T003 搭建 5.3.4.1 CommandParser 骨架

| 字段 | 内容 |
| --- | --- |
| 归属 | 02 组件 5.3.4.1 CommandParser |
| 类型 | 搭建 |
| 批次 | B1 |
| 执行者 | 示例实现者 |
| 验收人 | 示例用户 |
| 目标 | 建立 `src/parser.py` 骨架：`parse(argv)` 空实现、`_usage()` 返回用法文本 |
| 范围 | 只建 `src/parser.py`；不实现分支逻辑 |
| 输入 | 02 的 5.3.4.1 组件定义、5.3.2 IF-INT-001 / 002 / 003 / 006；03 的 7.2.4 |
| 产出 | 骨架代码、compileall 通过 |
| 完成判据（DoD） | `parse` 可调用并返回 text / exit_code 字典结构；`_usage` 文本与 03 的 F-302 一致 |
| 覆盖需求 | SSR001、SSR002 |
| 验收判据 | 无独立验收（验收在 T007） |
| 验证 | `python -c "import parser; print(parser._usage())"` 应打印用法行 |
| 证据 | T007 的 pytest 输出涵盖本任务接口 |
| 依赖 | T002 |
| 可并行 | 否 |
| 规模 | S |
| 风险 / 回滚 | 骨架期 parse 不处理任何命令，测试会红，属预期；回滚删文件重来 |

### T004 搭建 5.3.4.2 TaskRenderer 骨架

| 字段 | 内容 |
| --- | --- |
| 归属 | 02 组件 5.3.4.2 TaskRenderer |
| 类型 | 搭建 |
| 批次 | B1 |
| 执行者 | 示例实现者 |
| 验收人 | 示例用户 |
| 目标 | 建立 `src/renderer.py` 骨架：`render(todos)` 与 `_format_line(todo)` 空实现 |
| 范围 | 只建 `src/renderer.py`；不实现格式化 |
| 输入 | 02 的 5.3.4.2 组件定义、5.3.2 IF-INT-006；03 的 7.2.4 |
| 产出 | 骨架代码、compileall 通过 |
| 完成判据（DoD） | 两个函数可导入，签名与 03 的 6.3 一致 |
| 覆盖需求 | SSR002 |
| 验收判据 | 无独立验收（验收在 T008） |
| 验证 | `python -c "import renderer"` 无异常 |
| 证据 | T008 的 pytest 输出涵盖本任务接口 |
| 依赖 | T003 |
| 可并行 | 是 |
| 规模 | S |
| 风险 / 回滚 | 无；回滚删文件重来 |

### T005 填充 5.3.6.1 TaskFile / 8.2 task_file

| 字段 | 内容 |
| --- | --- |
| 归属 | 02 组件 5.3.6.1 TaskFile / 03 软件单元 8.2 task_file |
| 类型 | 填充 |
| 批次 | B2 |
| 执行者 | 示例实现者 |
| 验收人 | 示例用户 |
| 目标 | 实现 F-101 read、F-102 write、F-103 _validate 与 E-101 / E-102 / E-103 三个错误路径 |
| 范围 | 只改 `src/task_file.py`；不新增 02 / 03 未定义的公开接口 |
| 输入 | 03 的 8.2.1 说明、8.2.2.1–8.2.2.3 函数设计、7.2.4；02 的 5.7 EX-003 |
| 产出 | 实现代码、`tests/test_task_file.py`、pytest 通过 |
| 完成判据（DoD） | 三个函数与 8.2.2 一致；写入失败不破坏原文件；读取不修改文件；不修改传入列表 |
| 覆盖需求 | SSR001、SSR002 |
| 验收判据 | SSR001 第 4 条（重启后任务仍在）；SSR002 第 4 条（列出不修改文件）；验证方法：测试；ASIL：不适用 |
| 验证 | `python -m pytest tests/test_task_file.py -q` |
| 证据 | pytest 全绿输出，覆盖读回、损坏文件、写入失败三例，见 `tests/logs/pytest-task_file.log` |
| 依赖 | T001 |
| 可并行 | 否 |
| 规模 | M |
| 风险 / 回滚 | 原子替换在某些文件系统上语义不同；回滚到「写临时文件 + 失败保留原文件」的保守实现 |

### T006 填充 5.3.5.1 TaskStore / 8.2 store

| 字段 | 内容 |
| --- | --- |
| 归属 | 02 组件 5.3.5.1 TaskStore / 03 软件单元 8.2 store |
| 类型 | 填充 |
| 批次 | B2 |
| 执行者 | 示例实现者 |
| 验收人 | 示例用户 |
| 目标 | 实现 F-201 add、F-202 list、F-203 load、F-204 save 与 E-201 / E-202 / E-203 |
| 范围 | 只改 `src/store.py`；文件访问全部委托 TaskFile |
| 输入 | 03 的 8.2.1 说明、8.2.2.1–8.2.2.4 函数设计、7.2.3 函数关系；02 的 5.7 EX-002 / EX-003 |
| 产出 | 实现代码、`tests/test_store.py`、pytest 通过 |
| 完成判据（DoD） | id 唯一递增；title 非空；写失败后内存与磁盘一致；list 返回副本 |
| 覆盖需求 | SSR001、SSR002 |
| 验收判据 | SSR001 第 1–3 条（成功录入、空标题拒绝、编号不同）；SSR002 第 1–2 条（含编号与状态、顺序一致）；验证方法：测试；ASIL：不适用 |
| 验证 | `python -m pytest tests/test_store.py -q` |
| 证据 | pytest 全绿输出，见 `tests/logs/pytest-store.log` |
| 依赖 | T005 |
| 可并行 | 否 |
| 规模 | M |
| 风险 / 回滚 | 自增 id 在多次 load 后可能冲突；回滚用 `max(id)+1` 的保守算法 |

### T007 填充 5.3.4.1 CommandParser / 8.2 parser

| 字段 | 内容 |
| --- | --- |
| 归属 | 02 组件 5.3.4.1 CommandParser / 03 软件单元 8.2 parser |
| 类型 | 填充 |
| 批次 | B2 |
| 执行者 | 示例实现者 |
| 验收人 | 示例用户 |
| 目标 | 实现 F-301 parse 的两个分支与 F-302 _usage，覆盖 E-301 / E-302 / E-303 |
| 范围 | 只改 `src/parser.py`；不访问文件、不格式化列表 |
| 输入 | 03 的 8.2.1 说明、8.2.2.1–8.2.2.2 函数设计、7.3.4 时序图；02 的 5.7 EX-001 |
| 产出 | 实现代码、`tests/test_parser.py`、pytest 通过 |
| 完成判据（DoD） | 三条用法错误路径都返回用法文本与退出码 1；add / list 分发正确 |
| 覆盖需求 | SSR001、SSR002 |
| 验收判据 | SSR001 第 1、2 条（成功提示、空标题错误）；SSR002 第 3 条（空列表提示，退出码 0）；验证方法：测试；ASIL：不适用 |
| 验证 | `python -m pytest tests/test_parser.py -q` |
| 证据 | pytest 全绿输出（含三条用法错误例），见 `tests/logs/pytest-parser.log` |
| 依赖 | T006 |
| 可并行 | 否 |
| 规模 | M |
| 风险 / 回滚 | 新增子命令易漏改用法文本；回滚由 02 重新评审接口 |

### T008 填充 5.3.4.2 TaskRenderer / 8.2 renderer

| 字段 | 内容 |
| --- | --- |
| 归属 | 02 组件 5.3.4.2 TaskRenderer / 03 软件单元 8.2 renderer |
| 类型 | 填充 |
| 批次 | B2 |
| 执行者 | 示例实现者 |
| 验收人 | 示例用户 |
| 目标 | 实现 F-401 render 与 F-402 _format_line，含空列表提示 |
| 范围 | 只改 `src/renderer.py`；纯函数，不访问文件 |
| 输入 | 03 的 8.2.1 说明、8.2.2.1–8.2.2.2 函数设计、7.3.4 时序图；02 的 5.3.4.2 接口定义 |
| 产出 | 实现代码、`tests/test_renderer.py`、pytest 通过 |
| 完成判据（DoD） | 输出行数与任务数一致（空列表一行提示）；顺序与输入一致；不修改输入 |
| 覆盖需求 | SSR002 |
| 验收判据 | SSR002 第 1–3 条（编号/标题/完成状态、顺序一致、空列表提示）；验证方法：测试；ASIL：不适用 |
| 验证 | `python -m pytest tests/test_renderer.py -q` |
| 证据 | pytest 全绿输出，见 `tests/logs/pytest-renderer.log` |
| 依赖 | T007 |
| 可并行 | 否 |
| 规模 | S |
| 风险 / 回滚 | 输出格式变更会让脚本解析失败；回滚保留旧格式 |

## 覆盖映射

| 任务 | 软件需求 ID / 异常 | 证据位置 |
| --- | --- | --- |
| T001, T005 | SSR001、SSR002、EX-003 | `tests/logs/pytest-task_file.log` |
| T002, T006 | SSR001、SSR002、EX-002、EX-003 | `tests/logs/pytest-store.log` |
| T003, T007 | SSR001、SSR002、EX-001 | `tests/logs/pytest-parser.log` |
| T004, T008 | SSR002 | `tests/logs/pytest-renderer.log` |

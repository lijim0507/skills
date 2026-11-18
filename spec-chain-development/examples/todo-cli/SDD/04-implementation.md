# 04-implementation.md —— Todo CLI 执行编写

> 角色：实现者 ｜ 依据：03-design-<模块>.md（每模块一份）｜ 状态：已确认

## 执行说明

按批次执行；每批完成后跑验证，把命令和结果写进任务卡「证据」。

## 执行批次

| 批次 | 范围 | 退出条件 |
| --- | --- | --- |
| B1 | CommandParser、TaskStore、TaskRenderer | 三条命令冒烟通过 |

## 任务

- [ ] T001 [B1] 实现 CommandParser | REQ-TC-ADD-001
- [ ] T002 [B1] 实现 TaskStore | REQ-TC-ADD-001
- [ ] T003 [B1] 实现 TaskRenderer | REQ-TC-LIST-001

## 任务卡

### T001

- **归属**：CommandParser
- **批次**：B1
- **执行者**：示例实现者
- **验收人**：示例验收人
- **目标**：解析 add 与 list 子命令及其参数。
- **范围**：src/parser.py。
- **输入**：03-design-CommandParser.md 的函数设计。
- **产出**：parse 函数与 UsageError 类型。
- **完成判据（DoD）**：未知命令与缺参数都返回 UsageError；正常输入返回命令对象。
- **验收判据**：REQ-TC-ADD-001 的子条目在正常与空标题输入下成立。
- **验证**：pytest tests/test_parser.py
- **证据**：pytest tests/test_parser.py 输出 4 passed
- **依赖**：无
- **可并行**：是
- **规模**：小
- **风险**：无
- **回滚**：删除 src/parser.py

### T002

- **归属**：TaskStore
- **批次**：B1
- **执行者**：示例实现者
- **验收人**：示例验收人
- **目标**：新增与列出任务，并原子读写 JSON 文件。
- **范围**：src/store.py。
- **输入**：03-design-TaskStore.md 的函数设计。
- **产出**：add / list / load / save 四个函数。
- **完成判据（DoD）**：标题为空返回 ValidationError；文件损坏返回 StoreError；写入失败不破坏原文件。
- **验收判据**：REQ-TC-ADD-001 的创建与空标题子条目成立。
- **验证**：pytest tests/test_store.py
- **证据**：pytest tests/test_store.py 输出 5 passed
- **依赖**：T001
- **可并行**：否
- **规模**：中
- **风险**：文件损坏处理不完整
- **回滚**：删除 src/store.py

### T003

- **归属**：TaskRenderer
- **批次**：B1
- **执行者**：示例实现者
- **验收人**：示例验收人
- **目标**：按添加顺序输出任务列表。
- **范围**：src/renderer.py。
- **输入**：03-design-TaskRenderer.md 的函数设计。
- **产出**：render 函数。
- **完成判据（DoD）**：空列表输出空提示；非空列表带编号与完成状态；顺序稳定。
- **验收判据**：REQ-TC-LIST-001 的三个子条目成立。
- **验证**：pytest tests/test_renderer.py
- **证据**：pytest tests/test_renderer.py 输出 3 passed
- **依赖**：T002
- **可并行**：否
- **规模**：小
- **风险**：无
- **回滚**：删除 src/renderer.py

## 覆盖映射

| 任务 | REQ / 风险 | 证据位置 |
| --- | --- | --- |
| T001 | REQ-TC-ADD-001 | pytest tests/test_parser.py |
| T002 | REQ-TC-ADD-001 | pytest tests/test_store.py |
| T003 | REQ-TC-LIST-001 | pytest tests/test_renderer.py |

## 修订记录

| 版本 | 状态 | 变更内容 | 变更日期 | 更改人 | 批准人 |
| --- | --- | --- | --- | --- | --- |
| r1 | 已批准 | 依据 03-design-<模块>.md r1 建档 | 2026-11-11 | 示例用户 | 示例用户 |

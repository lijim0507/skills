---
name: spec-driven-development
description: 以规范驱动开发（SDD）约束软件变更：先定规格、经评审门批准后拆解任务，再逐步实施与收敛。用于项目建项、需求变更、方案变更等一切会改动代码的场景；不适用于纯问答、文档阅读或只读任务。
license: Apache-2.0
metadata:
  author: lijingyuan
  version: "2.0.0"
  tags:
    - sdd
    - spec
    - workflow
---
# 规范驱动开发（SDD）

## Description

以「先定规格、再动代码」的流程约束软件变更：每一步都落在文档上，每一次改动都要过评审门，保证变更可追溯、可验收、可收敛。

软件变更失控有两种典型形态，本流程各用一条机制堵住：

- **需求变更没经审批就溜进去了**——实现改着改着，实际行为已经和当初定好的不一样。用**落点判定**挡住：改动落在哪份文档，就从对应的门开始重走多远。
- **实现偷偷偏离了文档**——代码改完了，文档还写着旧的，没人发现。用**漂移三分类**收住：发现文档与实现不一致时，先分类，再决定改文档还是改代码。

项目建项时确定一套文档集，之后所有变更都在**同一套**上改和记录，不新开文档集：

```text
SDD/
├── 00-constitution.md      项目原则：可判定、编号、注明出处
├── 01-spec.md              只写 what / why
├── 02-plan.md              技术方案（how）
│   ├── 02-plan-research.md     Phase 0：消化所有 [NEEDS CLARIFICATION]
│   ├── 02-plan-data-model.md   Phase 1：实体、状态迁移
│   ├── 02-plan-contracts.md    Phase 1：接口契约
│   └── 02-plan-quickstart.md   Phase 1：验证场景
├── 03-tasks.md             任务 + 变更轮段 + Convergence 段
└── 04-converge.md          收敛报告 + 变更轮处置记录
```

**最要紧的一条边界**：spec 只写 what / why，凡「改了它需求不变」的内容一律进 plan。各文档职责与判据见 `references/doc-set.md`。

## When to use

适用于：

- 项目建项：绿地新项目，或为已有代码的项目补建文档集
- 一切会改动代码的变更请求：新增功能、修改现有行为、修复缺陷、重构
- 需求变更、方案变更、范围裁剪
- 用户明确要求走 SDD 流程，或提到「规范驱动」「先写规格」

## When NOT to use

不适用于：

- 纯问答、代码解释、阅读理解等不产生变更的任务
- 只读操作（查看日志、搜索代码、读取文件）
- 与代码变更无关的文档整理与格式调整

## Input

从对话上下文中获取以下信息：

- **变更请求**（必填）：要改什么、为什么改
- **目标项目或模块**（可选）：默认当前工作目录
- **既有文档集**（可选）：默认项目根下的 `SDD/`；已存在就先读它，不重建
- **约束条件**（可选）：期限、兼容性、硬件资源等

变更请求含糊时，用 `[NEEDS CLARIFICATION]` 或 `blocked` 显式标记并向用户确认，**不要猜**。项目还没有文档集时，先执行第 1 步建项。

## Instructions

1. **起步（仅建项时）**——绿地新项目：提取宪法 → 用户 ratify → spec → 门 1 → plan → 门 2 → tasks。棕地或回溯（已有代码、或已做完的项目）：以实现为事实源反推宪法与 spec，偏差进「待办与偏差登记」→ **逐条确认偏差判定**（只确认偏差，不确认正常内容）→ 走门 1 / 门 2。宪法与 spec 都是**提取**出来的，不是发明的；详见 `references/bootstrap.md`。每写完一份 spec，用 `python scripts/check_spec.py` 校验其结构。
2. **判落点**——收到变更请求后依次问，第一处「会变」的就是落点：

   | 问                                                         | 落点             | 重走范围                                                                       |
   | ---------------------------------------------------------- | ---------------- | ------------------------------------------------------------------------------ |
   | 验收场景会不会变？                                         | **spec**   | 门 1 → plan → 门 2 → tasks → analyze → checklist → implement → converge |
   | 方案会不会变？（引脚 / 外设 / 接口 / 数据模型 / 资源分配） | **plan**   | 门 2 → tasks → analyze → checklist → implement → converge                 |
   | 只是既有任务的增删改？                                     | **tasks**  | checklist → implement → converge                                             |
   | 都不涉及，只是实现修正？                                   | **仅实现** | converge                                                                       |

   两条补充：**判不准按上游**（当作 spec 处理——判错方向的代价不对称，把 spec 变更误判成 plan，等于需求变更未经审批溜过去了）；**跨多层取最高**（同一次变更同时触到 spec 和 plan 时按 spec 处理，重走范围必须覆盖最上游那处）。详细判法与依据见 `references/landing.md`。
3. **写受理单**——写进 `03-tasks.md` 新增变更轮段的开头，并用 `python scripts/check_intake.py` 自检「落点 ↔ 重走范围」是否自洽：

   ```markdown
   > - **落点**：spec（最高处）｜同时触及 plan（脚位 48→47）
   > - **重走范围**：门 1 → plan → 门 2 → tasks → analyze → checklist → implement → converge
   > - **判定依据**：`01-spec.md` US4 验收场景 3「回到 IDLE，白灯常亮」的语义由「灭态」改为「白常亮」
   > - **处置记录**：见 `04-converge.md` 变更轮
   ```
4. **随重走路径走**——从落点对应的第一道门开始；落点是 spec 或 plan 时，**受理单随第一道门一起受人审**，不要再另开一个「请确认落点」的停顿。主干如下（门 1 / 门 2 是人审门禁，analyze / checklist / converge 是三道质量机制，机制细节见 `references/quality-mechanisms.md`）：

   ```text
   constitution（建项一次，之后走 Governance 修订）
      ↓
   01-spec
      ↓
   门 1  ── reject → 退回 spec 修，重跑门 1
      ↓
   02-plan（+ Phase 0/1 子件）
      ↓
   门 2  ── reject → 退回 plan 修，重跑门 2
      ↓
   03-tasks
      ↓
   analyze ── 只读；发现问题回上游修，重跑直到干净
      ↓
   checklist ── 实现前门禁；有未勾选 → 停下询问
      ↓
   implement
      ↓
   converge ── 只追加；唯一写入是往 tasks.md 追加任务
      ↓
   Converged（tasks.md 逐字节不变）／ Tasks appended → 回 implement
   ```
5. **守住三条硬纪律**——三道机制各自有明确的写权限边界：

   | 机制          | 写权限                         | 发现问题时                   |
   | ------------- | ------------------------------ | ---------------------------- |
   | `checklist` | 评审者所有，`implement` 只读 | 停下询问，不得自己打勾       |
   | `analyze`   | **只读**，从不改文件     | 回上游修，重跑直到干净       |
   | `converge`  | **只追加**               | 变成新任务，不得改代码让它过 |

   **共同点：都不允许「就地改到通过」**，问题必须回到拥有它的地方解决。
6. **漂移先分类再动作**——发现「文档与实现不一致」时，**不是所有漂移都改文档**：

   | 类型                     | 判据                             | 处置                              |
   | ------------------------ | -------------------------------- | --------------------------------- |
   | **需求漂移**       | 验收场景变了                     | 改 spec → 走门 1 → 全流程重走   |
   | **实现漂移**       | 需求没变，实现没做到或做成了别的 | 改实现                            |
   | **放错位置的漂移** | 漂移的是本该属于 plan 的实现细节 | 搬到正确文档，**spec 不动** |

   第三类最容易被误判：「spec 写 GPIO21、实现是 GPIO19」的正确动作，是**把那行从 spec 删掉**搬进 plan，而不是改 spec 去对齐实现。详见 `references/drift.md`。
7. **维护任务状态**——三种状态：`[ ]` 未完成 ｜ `[x]` 已完成 ｜ `[~]` 已作废。作废一个任务时三处同时标记：原任务行标 `[~]`；原任务内容加删除线（**任务号与 FR 编号留在删除线外**，保持可检索）；下方一行 `⤷` 说明被谁取代、为什么。

   ```markdown
   - [~] T026 [P] [US1] ~~面板 WS2812 `main/test/drv_test.c`（busy/pass/fail/off 四态一次性设置）~~ | FR-040/041
         ⤷ r2 作废：灭态废除、busy 改蓝，被 T034 取代
   ```

   同时在变更轮段登记一份作废清单，并用 `python scripts/check_tasks.py` 校验（`[~]` 必须带理由与取代者）。
8. **范围裁剪**——裁掉或延期一个需求等于需求范围变了，即 **spec 落点**，一律走门 1。**FR 编号不重用**：原地标 `Deferred`（延期）或 `Cut`（不做），**绝不删号、绝不重分配**；写明**理由 + 裁决人 + 日期**；相关任务标 `[~]` 并注明「范围裁剪」。
9. **异常路径**——**门 reject**：退回该门上游修，修完重跑该门，不得带病继续。**converge 不收敛**：每轮发现数必须**严格递减**，某轮不降反增就立即停下回上游（说明在打转，通常是 spec / plan 本身有问题，继续跑只烧钱）。**blocked**：显式标记，写明卡在哪、等谁、等信息，不假装完成。
10. **禁止静默猜测**——同一原则的两层应用：spec 层不确定就标 `[NEEDS CLARIFICATION]`，不许猜（猜错参数的代价——重新打板、返工——在这个标记面前被前置了）；执行层不确定就标 `blocked`，不许猜。

## Output

- 更新后的文档集 `SDD/`：按落点重走后的 `01-spec.md` / `02-plan.md` / `03-tasks.md`，以及新增的变更轮段与受理单
- 按任务清单完成的代码变更：任务逐条勾选 `[x]`，作废的标 `[~]` 并登记进作废清单
- `04-converge.md`：收敛报告与变更轮处置记录，结论为 `Converged`（`tasks.md` 逐字节不变）或「Tasks appended」（追加任务后回 implement）
- 完成判据 **`Done When`**：`tasks.md` 中所有任务均为 `[x]` 或 `[~]`（无 `[ ]`），且实现已对照规格、方案与测试覆盖完成验证

## 资源

- `references/doc-set.md`——文档集与职责边界
- `references/landing.md`——落点判定与受理单
- `references/quality-mechanisms.md`——checklist / analyze / converge
- `references/drift.md`——漂移三分类
- `references/bootstrap.md`——绿地 / 棕地起步
- `references/templates/`——`00` ~ `04` 各文档模板
- `scripts/check_spec.py`——spec 结构校验
- `scripts/check_intake.py`——受理单自洽校验（落点 ↔ 重走范围）
- `scripts/check_tasks.py`——任务状态校验（`[~]` 必须带理由与取代者）

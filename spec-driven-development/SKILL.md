---
name: spec-driven-development
description: 以规范驱动开发（SDD）流程约束软件变更：先写变更规格，经用户确认后拆解任务，再逐步实施与验收。当用户要求修改、新增或重构代码且希望流程受控、可追溯时使用；不适用于纯问答、文档阅读或与代码变更无关的任务。
license: Apache-2.0
metadata:
  author: lijingyuan
  version: "1.0.0"
  tags:
    - sdd
    - spec
    - workflow
---

# 规范驱动开发（SDD）

## Description

以"先写规格、再动代码"的流程约束软件变更，保证每次修改有据可查、可验收、可回溯。

## When to use

适用于：

- 新增功能、修改现有行为、修复缺陷
- 重构等一切会改动代码的任务
- 用户明确要求走 SDD 流程，或提到"规范驱动"、"先写规格"

## When NOT to use

不适用于：

- 纯问答、代码解释、阅读理解等不产生变更的任务
- 只读操作（查看日志、搜索代码）
- 用户明确要求跳过流程直接修改的小改动

## Input

从对话上下文中获取以下信息：

- **变更请求**（必填）：要改什么、为什么改
- **目标仓库或模块**（可选）：默认当前工作目录
- **约束条件**（可选）：期限、兼容性要求等

若变更请求含糊，先向用户确认目标再进入规格编写。

## Instructions

1. 建立规格目录：在仓库根创建 `specs/<变更名>/`，变更名使用 kebab-case
2. 编写规格：按 `resources/prompt.md` 的模板写 `spec.md`，覆盖背景、目标、范围、非目标、影响面、验收标准六个章节
3. 规格门禁：运行以下命令，必须通过才能进入下一步

   ```bash
   python scripts/check_spec.py specs/<变更名>/spec.md
   ```

4. 用户确认：把规格摘要呈现给用户，等待明确批准；未批准前不得修改任何代码（受 `resources/config.yaml` 的 `require_approval` 控制）
5. 任务拆解：把规格拆成带验证步骤的任务清单，写入 `specs/<变更名>/tasks.md`；任务数不超过配置中的 `max_tasks`
6. 逐任务实施：每完成一个任务立即勾选并运行其验证步骤；验证失败时停下修复或回滚，不带病前进
7. 验收与归档：对照验收标准逐条核对，更新 README 与 CHANGELOG；`spec.md` 与 `tasks.md` 保留在 specs 目录作为变更记录

## Output

- `specs/<变更名>/spec.md` 与 `tasks.md`
- 按任务清单完成的代码变更
- 更新后的 README 与 CHANGELOG
- 验收结论：每条验收标准的通过情况
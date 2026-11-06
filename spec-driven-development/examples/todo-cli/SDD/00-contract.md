# 00-contract.md —— Todo CLI 项目契约

> 作者：人（AI 起草） ｜ 版本：r1 ｜ 状态：已确认 ｜ 依据：无（项目自建）

## 1. Development Philosophy（开发原则）

### Principle: 离线优先

**Rule:**
- MUST 在无网络环境下完成全部功能
- MUST NOT 发起网络请求

**Verification:**
- 自动：断网跑 `pytest` 与 CLI 冒烟
- 人工：review 依赖清单

**Exception:**
- 无

**Rationale:**
终端开发者常在受限网络环境工作

## 2. Architecture Governance（架构治理）

### Principle: 公共接口边界

**Rule:**
- MUST 只通过 `02-plan-contracts.md` 列出的公开接口跨模块调用
- MUST NOT 直接访问其他模块的内部函数或数据

**Verification:**
- 自动：`tests/test_contracts.py`
- 人工：review import 关系

**Exception:**
- 无

**Rationale:**
防止隐式依赖

## 3. Code Quality（代码质量）

### Principle: 失败不破坏数据

**Rule:**
- MUST 用临时文件 + 原子替换写入
- MUST NOT 在写入失败时改动原文件

**Verification:**
- 自动：故障注入测试 `tests/test_store.py`
- 人工：review 写路径

**Exception:**
- 无

**Rationale:**
早期版本直接覆写导致数据丢失

## 4. Testing & Verification（测试与验证）

### Principle: 行为变更必须有验证

**Rule:**
- MUST 为每个行为变更提供可复跑命令
- MUST NOT 把没跑过的命令写成「通过」

**Verification:**
- 自动：CI 跑 `pytest`
- 人工：对照 03 任务卡的「验证 / 证据」

**Exception:**
- 无法在主机验证时，MUST 写明原因与替代验证

**Rationale:**
证据可复核

## 5. AI Development Governance（AI 开发治理）

### Principle: 不越界

**Rule:**
- MUST 只改任务卡范围内的文件
- MUST NOT 扩大需求范围、改无关文件、伪造编译或测试结果

**Verification:**
- 自动：CI 编译 / 测试
- 人工：review diff 与任务卡范围

**Exception:**
- 无

**Rationale:**
防止越界与虚假完成

## 6. Change Management（变更管理）

### Principle: 接口与依赖变更受控

**Rule:**
- MUST 公共接口或依赖变更在 `02-plan.md` 说明影响并取得人批准

**Verification:**
- 人工：对照「契约合规」与修订记录

**Exception:**
- 紧急修复事后补记，由人批准

**Rationale:**
变更可追溯

## 7. Governance（治理）

### Principle: 规范变更受控

**Rule:**
- MUST 规范修改经团队评审
- SHOULD 定期审查规范有效性

**Verification:**
- 人工：评审记录 / 修订记录

**Exception:**
- 无

**Rationale:**
保证契约本身可维护

## 修订记录

| 版本 | 日期 | 修订理由 | 批准人 |
| --- | --- | --- | --- |
| v1 | 2026-10-19 | 建档 | 示例用户 |

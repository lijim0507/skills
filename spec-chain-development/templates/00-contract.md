# 00-contract.md —— <项目名> 项目契约

> 作者：人（AI 起草） ｜ 版本：r1 ｜ 状态：待确认 ｜ 依据：<团队宪法 vX / 无>

本项目所有改动都要遵守的治理规则。它约束决策，不替 02 做技术决策。
每条规则必须可判定；写不出 `Verification` 的规则不进本文件。

**级别**：MUST / MUST NOT 强制；SHOULD 默认要求，例外需写明理由；MAY 可选。

## 1. Development Philosophy（开发原则）

### Principle: <规则名>

**Rule:**
- MUST <…>
- MUST NOT <…>

**Verification:**
- 自动：<命令 / 脚本>
- 人工：<评审步骤>

**Exception:**
- <谁批准、记在哪；无例外写「无」>

**Rationale:**
<为什么需要这条>

## 2. Architecture Governance（架构治理）

### Principle: <规则名>

<同上>

## 3. Code Quality（代码质量）

### Principle: <规则名>

<同上>

## 4. Testing & Verification（测试与验证）

### Principle: <规则名>

<同上>

## 5. AI Development Governance（AI 开发治理）

### Principle: 修改前理解上下文

**Rule:**
- MUST 修改前读相关 Spec / Plan
- MUST NOT 扩大需求范围或改无关文件
- MUST NOT 伪造编译、测试结果

**Verification:**
- 自动：CI 编译 / 测试
- 人工：review diff 与任务卡范围

**Exception:**
- 无

**Rationale:**
防止越界与虚假完成

## 6. Change Management（变更管理）

### Principle: <规则名>

<同上>

## 7. Governance（治理）

### Principle: 规范变更受控

**Rule:**
- MUST 规范修改经团队评审
- MUST 在规范与项目实际冲突时明确处理
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
| v1 | <YYYY-MM-DD> | 建档 | <名字> |

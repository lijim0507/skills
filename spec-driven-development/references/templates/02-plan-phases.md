# Phase 0 / Phase 1 子件

`02-plan.md` 之外，plan 阶段还产出四份子件。**按需生成**——变更不涉及某类关切时，对应子件不必存在。

## Phase 0：`02-plan-research.md`

把 `01-spec.md` 里的每一条 `[NEEDS CLARIFICATION]` 消化掉。每条决策写成：

````markdown
## 决策 <N>：<决策标题>（解决 FR-xxx / SC-xxx）

**结论**：<选了什么>

**理由**：<为什么>

**被否决的方案**：
- <方案 A> —— 否决理由：<…>
- <方案 B> —— 否决理由：<…>
````

> **「被否决的方案」不能省。** 它记录了「当时为什么不那样做」，是将来回头质疑决策时的唯一依据。省掉它，三个月后就会有人把已否决的方案重新提一遍。

**收口要求**：Phase 0 结束时，`01-spec.md` 里不应再有未消化的 `[NEEDS CLARIFICATION]`。

## Phase 1：三份设计产物

三者按需生成，缺一不可的前提是变更确实涉及对应关切。

### `02-plan-data-model.md`

````markdown
# Data Model：<项目名>

## Entity: <实体名>

| 字段 | 类型 | 说明 |
|---|---|---|
| | | |

## 状态转换

```text
<IDLE> ──按键──> <RUN> ──完成──> <RESULT>
```
````

### `02-plan-contracts.md`

````markdown
# Contracts：<项目名>

> **按执行上下文分层标注**——`@context: isr` 与 `@context: task` 分开写。
> 混排的代价：ISR 里误调不会编译报错，只会在最坏情况暴露。

## @context: isr

### `can_dispatch()`

| 项 | 说明 |
|---|---|
| 签名 | `void can_dispatch(const can_frame_t *f)` |
| 前置 | 仅中断上下文调用 |
| 禁止 | 不得调用任何 Flash 擦写 / 阻塞 API |

## @context: task

### `download_action()`

<…>
````

### `02-plan-quickstart.md`

````markdown
# Quickstart / 验证场景：<项目名>

## 场景 1：<名称>

- **前置**：<…>
- **操作**：<…>
- **期望**：<…>
- **对应**：FR-xxx / SC-xxx
````
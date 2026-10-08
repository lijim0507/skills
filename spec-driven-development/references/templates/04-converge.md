# 04 · 收敛报告（converge）

> **只追加**：从不编辑或删除代码；唯一可能的写入是往 `tasks.md` 追加任务。
> **只在当前 `tasks.md` 上的 implement 跑过之后才可运行。**
> **终止条件**：每轮发现数必须严格递减。某轮不降反增 → 立即停下回上游。

## 一、已收敛项（对码证据）

| # | spec / tasks 条目 | 实现证据 |
|---|---|---|
| | | |

## 二、发现与处置（第 <N> 轮，按严重度）

```text
[HIGH]   #1 <发现标题>
         spec <出处> / 实现 <出处>
         → <处置>
[MEDIUM] #2 <…>
[LOW]    #3 <…>
```

## 三、收敛结论

<二选一>

- 情况一：`Converged — the implementation satisfies the spec, plan, and tasks.`
  判据：`tasks.md` **逐字节不变**
- 情况二：`Tasks appended`（<N> 项，写入 `tasks.md` 的 Convergence 段 T9xx~T9yy）
  → 再跑 `implement`，再跑 `converge`

## 四、变更轮（<日期> rN：<一句话摘要>）

<这里记由用户发起的变更（非 converge 扫出的缺口）。>

- **漂移分类**：<需求漂移 / 实现漂移 / 放错位置的漂移 / 新需求>
- **处置**：<…>
- **决策记录**：<grilling / 讨论的结论>
- **显式验证项**：<需要实测证据的项>

## 来源

- `01-spec.md` / `02-plan*.md` / `03-tasks.md` —— 比对上游
- <实现侧比对对象>
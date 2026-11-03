# Todo CLI 示例（v3 角色卡版）

这是一套跑通的最小 SDD 文档集，用来演示“角色卡 + 流程 + 文档”的交接，不是让你照抄字段。

- `SDD/00-constitution.md`：项目宪法。
- `SDD/01-spec.md`：产品经理角色卡产物。定位、范围外、用户故事、FR、外部契约。
- `SDD/02-plan.md`：技术总监角色卡产物。模块、数据、决策、质量、风险、验证。
- `SDD/02-plan-research.md`：关键决策与被否决方案。
- `SDD/02-plan-data-model.md`：实体、状态、写权限。
- `SDD/02-plan-contracts.md`：模块间的内部契约。
- `SDD/03-tasks.md`：任务负责人角色卡产物。批次、任务卡、覆盖映射、评审记录。
- `SDD/04-converge.md`：收敛与验收记录。

## 怎么用它

1. 先读 `01-spec.md` 的「交接给技术总监」，再看 `02-plan.md` 的「需求兑现核对」。
2. 再读 `02-plan.md` 的「交接给任务拆解」，对照 `03-tasks.md` 的任务卡。
3. 最后看 `04-converge.md` 怎么把验收证据落下来。

## 验证

在技能根目录运行：

```bash
python scripts/check_spec.py  examples/todo-cli/SDD/01-spec.md
python scripts/check_tasks.py examples/todo-cli/SDD/03-tasks.md
python scripts/check_chain.py examples/todo-cli/SDD
python scripts/check_plan.py  examples/todo-cli/SDD
```

四个检查应当全部通过。

# Todo CLI 示例

这是一套跑通的最小 SDD 文档集，用来演示三顶帽子怎么交接，不是让你照抄字段。

- `SDD/01-spec.md`：产品经理视角。问题、目标消费者、非目标、故事、外部契约、验收场景。
- `SDD/02-plan.md`：技术总监视角。方案总览、逐条可行性、模块边界、质量属性、风险与回滚、验证手段。
- `SDD/02-plan-contracts.md`：模块间的内部契约。
- `SDD/03-tasks.md`：任务负责人视角。分配说明、执行批次、任务卡（含执行者与 DoD）。
- `SDD/04-converge.md`：收敛与验收记录。

## 怎么用它

1. 先读 `01-spec.md` 的「交接给技术总监」，再看 `02-plan.md` 的「需求可行性核对」。
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

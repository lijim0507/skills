# Todo CLI 示例（四角色版）

这是一套跑通的最小 SDD 文档集，用来演示“角色卡 + 流程 + 交接”的链路，不是让你照抄字段。

- `SDD/00-contract.md`：项目契约。长期规则与边界，项目初始化时写一次。
- `SDD/01-spec.md`：产品经理角色卡产物。定位、范围外、用户故事、FR、外部契约。
- `SDD/02-plan.md`：技术总监角色卡产物。模块、数据、决策、质量、风险、验证。
- `SDD/02-plan-research.md`：关键决策与被否决方案。
- `SDD/02-plan-data-model.md`：实体、状态、写权限。
- `SDD/02-plan-contracts.md`：模块间的内部契约。
- `SDD/03-tasks.md`：任务负责人角色卡产物。批次、任务卡、覆盖映射；执行证据也落在这里。

## 怎么用它

1. 先读 `00-contract.md` 的项目约束，再读 `01-spec.md` 的产品定位。
2. 读 `01-spec.md` 的「交接给技术总监」，对照 `02-plan.md` 的「需求兑现核对」。
3. 读 `02-plan.md` 的「交接给任务拆解」，对照 `03-tasks.md` 的任务卡。
4. 看 `03-tasks.md` 里每张卡的「验证 / 证据」栏，这是人验收时要抽查的东西。

## 验证

在技能根目录运行：

```bash
python scripts/check_spec.py  examples/todo-cli/SDD/01-spec.md
python scripts/check_tasks.py examples/todo-cli/SDD/03-tasks.md
python scripts/check_chain.py examples/todo-cli/SDD
python scripts/check_plan.py  examples/todo-cli/SDD
```

四道检查应当全部通过。

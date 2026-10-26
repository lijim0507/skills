# 机器检查

```bash
python scripts/check_spec.py  <SDD>/01-spec.md
python scripts/check_plan.py  <SDD>
python scripts/check_tasks.py <SDD>/03-tasks.md
python scripts/check_chain.py <SDD>
python scripts/check_skill.py <技能目录>
```

## 输出怎么读

- 「结构检查通过 · 语义未验证」= 只证明章节、编号、链条、字段齐全
- 不覆盖：需求可验收性、方案可行性、任务可执行性、模板语义
- 脚本绿 ≠ 门通过；门只认独立评审 + 人签字

## 会报错的情况

- 占位符未清理（待填 / TODO / <…>）
- 缺少文档头角色行
- 章节顺序与模板不一致
- 01 正文引用了未定义的 FR
- 任务卡字段值为空

## 回归

改技能后跑 `examples/todo-cli` 四道检查 + 空话规格探针（必须失败）。

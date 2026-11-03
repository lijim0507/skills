# 机器检查与人工检查

## 机器检查

```bash
python scripts/check_spec.py  <SDD>/01-spec.md
python scripts/check_plan.py  <SDD>
python scripts/check_tasks.py <SDD>/03-tasks.md
python scripts/check_chain.py <SDD>
python scripts/check_skill.py <技能目录>
python scripts/check_loadsets.py <技能目录>
```

## 输出怎么读

- 「结构检查通过 · 语义未验证」= 只证明章节、编号、链条、字段齐全
- 不覆盖：需求可验收性、方案可行性、任务可执行性、模板语义、角色边界
- 脚本绿 ≠ 门通过；门只认门简报 + 独立评审 + 人签字
- 装载集在预算内只证明读的文件没超预算，不证明读得对、读得全

## 角色边界检查

脚本不检查角色越界，必须人工回答：

- 我写了不属于我的文档吗？
- 我做了不属于我的决定吗？
- 我读了不该读的内容吗？
- 我把上游缺口在下游私了吗？

## 评审记录

评审者必须写「查了哪些项、发现几条、每条在哪」。`未发现问题` 不算结论；至少写查了哪些项、0 条阻断。

## 模板符合度

脚本不检查模板符合度。交门前人工对照 `templates/` 检查：

- 章节顺序是否与模板一致
- 必填字段是否齐全
- 版本 / 状态是否写在文档头

## 回归

改技能后跑 `examples/todo-cli` 四道检查 + `check_skill.py` + `check_loadsets.py` + 空话规格探针（必须失败）。

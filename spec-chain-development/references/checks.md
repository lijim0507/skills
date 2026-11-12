# 机器检查与人工检查

## 机器检查

```bash
python scripts/check_requirements.py    <SDD>/01-requirements.md
python scripts/check_architecture.py    <SDD>
python scripts/check_design.py          <SDD>
python scripts/check_implementation.py  <SDD>/04-implementation.md
python scripts/check_chain.py           <SDD>
python scripts/check_skill.py           <技能目录>
python scripts/check_loadsets.py        <技能目录>
```

## 输出怎么读

- 「结构检查通过 · 语义未验证」= 只证明章节、编号、链条、字段齐全
- 不覆盖：需求可验收性、架构可行性、设计可实现性、任务可执行性、模板语义、角色边界
- 脚本绿 ≠ 可以开工；开工由人启动
- 装载集在预算内只证明读的文件没超预算，不证明读得对、读得全

## 人工检查（确认前）

- **01**：需求清单与正文编号一致；每条 REQ 有优先级与来源；输入与输出覆盖外部边界；子条目可观察、可验证；未决项标清是否阻塞
- **02**：每条 REQ 有落点模块；模块清单与契约一一对应；依赖矩阵与模块清单一致；依赖无环；资源与调度、异常清单有内容；非功能有目标与验证
- **03**：02 每个模块在 8.2 函数设计下有分组（函数 ID、所在文件）；每个公开接口有对应函数；参数 / 动态特性 / 数据质量已交代；错误处理与不变量齐全；交接给实现有源代码文件清单
- **04**：每条 REQ / 风险有任务覆盖；任务卡自足；没有 `blocked` 未解

## 交接检查

- 产物末节有「交接给下一角色」，写的是判断，不是正文摘要
- 文档头状态为 `已确认`
- 下游没有替上游改正文；发现缺口有回交记录

## 写之前问四句

1. 我写了不属于我的文档吗？
2. 我做了不属于我的决定吗？
3. 我读了不该读的内容吗？
4. 我把上游缺口在下游私了吗？

任何一句“是”，停，按角色卡的退回规则处理。

## 模板符合度

脚本不检查模板符合度。确认前人工对照 `templates/` 检查：

- 章节顺序是否与模板一致
- 必填字段是否齐全
- 版本 / 状态是否写在文档头

## 回归

改技能后跑 `examples/todo-cli` 四道检查 + `check_skill.py` + `check_loadsets.py` + 空话规格探针（必须失败）。

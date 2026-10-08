# spec-driven-development

以规范驱动开发（SDD）约束软件变更：**落点判定**决定重走范围，**评审门 + 三道质量机制**把关，**漂移三分类**处置不一致。

## 安装

1. 将 `spec-driven-development/` 目录复制到你的 skills 目录
2. 无额外依赖（脚本仅用 Python 标准库）

## 核心思想

文档集是一串上下游依赖：`spec → plan → tasks → 实现`。改动落在链条上的位置，决定了下游有多少东西可能失效——所以也决定了要从哪重走。

> **位置决定成本。**

| 落点 | 重走范围 |
|---|---|
| spec | 门 1 → plan → 门 2 → tasks → analyze → checklist → implement → converge |
| plan | 门 2 → tasks → analyze → checklist → implement → converge |
| tasks | checklist → implement → converge |
| 仅实现 | converge |

## 使用方法

对 Agent 说「按 SDD 流程改 xxx」，Agent 会：

1. 判落点（锚点是**验收场景变没变**；判不准按上游）
2. 写受理单（落点，含同时触及 + 重走范围 + 判定依据）
3. 从落点对应的第一道门开始，顺流重走

## 三道质量机制

| 机制 | 检查对象 | 写权限 |
|---|---|---|
| `checklist` | 需求本身的质量 | 评审者所有，implement 只读 |
| `analyze` | 文档之间是否自洽 | 只读，从不改文件 |
| `converge` | 实现有没有背叛文档 | 只追加 |

**共同点：都不允许「就地改到通过」。**

## 脚本

```bash
python scripts/check_spec.py  <01-spec.md>    # 规格结构校验
python scripts/check_intake.py <03-tasks.md>  # 受理单自洽（落点 ↔ 重走范围）
python scripts/check_tasks.py  <03-tasks.md>  # 任务状态与作废格式
```

## 目录结构

```text
spec-driven-development/
├── SKILL.md                        流程主干 + agent 行为
├── metadata.json
├── references/
│   ├── doc-set.md                  文档集与职责边界
│   ├── landing.md                  落点判定与受理单
│   ├── quality-mechanisms.md       门 + checklist / analyze / converge
│   ├── drift.md                    漂移三分类
│   ├── bootstrap.md                绿地 / 棕地起步
│   └── templates/
│       ├── 00-constitution.md
│       ├── 01-spec.md
│       ├── 02-plan.md
│       ├── 02-plan-research.md
│       ├── 02-plan-data-model.md
│       ├── 02-plan-contracts.md
│       ├── 03-tasks.md
│       └── 04-converge.md
├── scripts/
│   ├── check_spec.py
│   ├── check_intake.py
│   └── check_tasks.py
├── examples/change-round.md        一次变更轮的完整走法
├── tests/
├── README.md
└── CHANGELOG.md
```

## 模板的权威来源

`references/templates/` 里的模板只在**起步时**用来生成文档集。

**若与知识库中实际项目的 SDD 文档不一致，以知识库为准。** 这样 skill 能独立安装，又不会变成第二事实源。

## 完整示例

见 `examples/change-round.md`——用真实项目的一次变更轮（面板灯语义重排 + 脚位 47）走完判定 → 受理 → 重走 → 作废 → 收敛。
# spec-driven-development

以规范驱动开发（SDD）约束软件变更：**一个判据**决定落点与重走范围，**人审门与机器守卫**两类关卡把关，**每个声明都挂证据**。

## 安装

1. 将 `spec-driven-development/` 目录复制到你的 skills 目录
2. 无额外依赖（脚本仅用 Python 标准库；`check_landing.py` 需要目标项目是 git 仓库）

## 模型：三样东西，其余都是推论

| 内核 | 内容 |
|---|---|
| **一个判据** | 改它，验收场景变没变？——用于落点判定、漂移分类、范围裁剪、内容归属 |
| **一条链** | `spec → plan → tasks → 实现`，位置决定成本 |
| **一份证据** | 每个「已完成 / 已通过」的声明都要挂可核对的证据；谁写什么由写权限划定 |

**唯一权威**：落点表、重走范围、状态机、写权限表都在 `SKILL.md` 的「流程模型（唯一权威）」一节。`references/*` 与本文只解释、不复述——要改这些表时只改一处。
> 设计由来、为什么这样划写权限、两次真实事故：见 `references/rationale.md`（人读；agent 执行流程不需要）。


## 使用方法

对 Agent 说「按 SDD 流程改 xxx」，Agent 会：

1. 判落点（锚点是**验收场景变没变**；判不准按上游）
2. 写受理单（五栏：落点 / 验收场景 / 重走范围 / 判定依据 / 处置记录）
3. 从落点对应的第一道门开始顺流重走；**门是阻塞点，必须停下等人工 approve**，并把结论（`approve` + 裁决人 + 日期）按规则写入被审文档或受理单

> **规模下限**：单个文件、不改变任何外部可观察行为的小改（错别字、注释、日志文案、格式化），且用户没有点名 SDD，不走本流程。项目还没有文档集时，agent 会先问你要不要建，不建就退出本流程。

## 关卡

| 关卡 | 谁判 | 写权限 |
|---|---|---|
| 门 1 / 门 2 | 人 approve / reject | 清单与结论行只由评审者写；**必须留下「人批准」记录**（approve + 裁决人 + 日期），`check_gate.py` 会校验——但它只能拦「待审 / reject / 占位符」，署名是不是真人查不出，得靠人守 |
| `analyze` | agent / 脚本 | 只写 `03-tasks.md` 的「analyze 交叉检查」一节 |
| `checklist` | 评审者（清单在门 1 内） | implement 前只读复核，不得自己打勾 |
| `converge` | agent | 只追加任务，不改代码与文档正文 |

**共同点：都不允许「就地改到通过」。**
> 门结论的落点只有两处：**首轮**写在被审文档的门小节里（门 1 在 `01-spec.md`、门 2 在 `02-plan.md`）；**变更轮**写在受理单里——受理单就是这个变更轮的人审材料。`check_gate.py` 两处都查。

## 脚本

```bash
python scripts/check_spec.py    <项目>/SDD/01-spec.md      # 规格结构
python scripts/check_intake.py  <项目>/SDD/03-tasks.md     # 受理单自洽（落点 ↔ 重走范围 ↔ 验收场景）
python scripts/check_tasks.py   <项目>/SDD/03-tasks.md     # 任务状态与作废格式
python scripts/check_landing.py <项目>/SDD/01-spec.md <项目>/SDD/03-tasks.md [--since REF]
python scripts/check_gate.py    <项目>/SDD/03-tasks.md [--spec 01-spec.md] [--plan 02-plan.md]  # 门的「人批准」记录
```

脚本在**技能目录**内，不在目标项目里——用绝对路径，或先进入技能目录再运行。

## 目录结构

```text
spec-driven-development/
├── SKILL.md                        流程模型（唯一权威）+ agent 行为
├── metadata.json
├── references/
│   ├── doc-set.md                  文档集、职责边界、内容归属判据
│   ├── landing.md                  落点判定怎么用、受理单
│   ├── quality-mechanisms.md       两类关卡：门与机器守卫
│   ├── drift.md                    判据的第二个调用点：漂移三分类
│   ├── bootstrap.md                绿地 / 棕地 / 宪法修订
│   ├── rationale.md                设计说明与真实事故（给人读的）
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
│   ├── check_tasks.py
│   ├── check_landing.py
│   └── check_gate.py
├── examples/change-round.md        一次变更轮的完整走法
├── tests/
├── README.md
└── CHANGELOG.md
```

## 模板的权威来源

`references/templates/` 里的模板只在**起步时**用来生成文档集，用完删掉示例段。

**若与项目里已有的 SDD 文档不一致，以项目文档为准。** 这样 skill 能独立安装，又不会变成第二事实源。

## 完整示例

见 `examples/change-round.md`——用真实项目的一次变更轮（面板灯语义重排 + 脚位 47）走完判定 → 受理 → 重走 → 机器兜底 → 作废 → 收敛。

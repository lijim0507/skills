# Todo CLI 示例（四阶段版）

这是一套跑通的最小 SDD 文档集，用来演示“一阶段一角色一文档 + 交接与追溯”的链路，不是让你照抄字段。

- `SDD/00-contract.md`：项目契约。长期规则与边界，项目初始化时写一次。
- `SDD/01-requirements.md`：需求分析师产物（SWE.1 结构）。概述、需求清单、需求间依赖、输入与输出、软件需求；每条 REQ 带需求类别、来源与验证准则；末尾追溯分析与修订记录。
- `SDD/02-architecture.md`：架构师产物（SWE.2 结构）。简介、资源（硬件 / 软件环境 / 外部系统）、沟通计划、软件分解（数据定义 / 模块清单 / 接口 / 依赖矩阵）、动态行为、资源消耗目标、软件调度机制、异常清单、假设和约束、模块契约、追溯分析。
- `SDD/03-design-<模块>.md`：详细设计师产物（SWE.3 结构，每模块一份）。组件描述、接口、静态 / 动态特性、8.2 软件单元（单元说明、函数编号 / 所在文件）、可追溯性。
- `SDD/04-implementation.md`：实现者产物。执行批次、任务卡、覆盖映射、验证与证据。

追溯链：

```
REQ（01）→ 模块 / 公开接口（02）→ 函数（03）→ 任务（04）→ 验证证据
```

## 怎么用它

1. 先读 `00-contract.md` 的项目约束，再读 `01-requirements.md` 的 REQ 与「交接给架构」。
2. 读 `02-architecture.md` 的模块清单和每个模块的「覆盖 REQ」，确认每条 REQ 都有落点。
3. 读 `03-design-<模块>.md`（每模块一份），确认软件单元与函数设计齐全。
4. 读 `04-implementation.md` 的任务卡，确认每条 REQ 都被任务覆盖，且「验证 / 证据」可复跑。
5. 人按 `01-requirements.md` 的子条目验收，抽查 `04-implementation.md` 的证据。

## 验证

在技能根目录运行：

```bash
python scripts/check_requirements.py    examples/todo-cli/SDD/01-requirements.md
python scripts/check_architecture.py    examples/todo-cli/SDD
python scripts/check_design.py          examples/todo-cli/SDD
python scripts/check_implementation.py  examples/todo-cli/SDD/04-implementation.md
python scripts/check_chain.py           examples/todo-cli/SDD
```

五道检查应当全部通过。

# Todo CLI 示例（四阶段版）

这是一套跑通的最小 SDD 文档集，用来演示“一阶段一角色一文档 + 交接与追溯”的链路，不是让你照抄字段。

- `SDD/00-contract.md`：项目契约。长期规则与边界，项目初始化时写一次。本示例直接沿用 `templates/00-contract.md` 的默认规则（其中 C 命名与分层约定是为嵌入式项目准备的，换成 Python / 其他栈时应在这一步改写，示例未改写）。
- `SDD/01-requirements.md`：需求分析师产物（SWE.1 结构）。修订记录、概述（目的 / 范围 / 术语 / 参考）、软件需求（3.1.1 清单、3.1.2 依赖、3.2 交互框图、3.3 需求卡）、追溯分析；每条 SSR 是模板式需求卡（含需求类别、目标阶段、ASIL、来源、需求分析、验证准则、验证方法）。
- `SDD/02-architecture.md`：架构师产物（SWE.2 结构）。简介、资源、沟通计划、软件架构设计（5.1 描述、5.2 外部接口、5.3 分解：数据定义 / 组件间接口 / 依赖矩阵 / 5.3.4–5.3.6 三层组件定义，每个组件写「覆盖需求」+ 描述 + 时序 + 接口定义）、5.4 动态行为（按阶段分节，每节一张 mermaid）、5.5 资源消耗、5.6 调度、5.7 异常、5.8 假设、生产运行、追溯分析。
- `SDD/03-design-<组件>.md`：详细设计师产物（SWE.3 结构，每个 02 组件一份）。组件描述、接口（数据结构 / 变量 / 参数 / 外部函数）、组件分解、静态特性（框架图 / 函数列表 / 函数关系 / 源代码文件清单）、动态特性、8.2 软件单元（单元说明 + 函数设计表）、可追溯性、附录（数据质量 / 交接给实现）。
- `SDD/04-implementation.md`：实现者产物。执行说明（两段式自底向上）、执行批次、任务索引、任务卡、覆盖映射。

追溯链：

```
SSR（01）→ 组件 / 公开接口（02）→ 函数（03）→ 任务（04）→ 验证证据
```

## 怎么用它

1. 先读 `00-contract.md` 的项目约束，再读 `01-requirements.md` 的 3.1.1 清单与 3.3 需求卡，确认每条 SSR 的验证准则可判。
2. 读 `02-architecture.md` 的 5.3.4 / 5.3.5 / 5.3.6 三层组件定义，逐个确认每个组件都写了「覆盖需求」，没有 SSR 落空。
3. 读 `03-design-<组件>.md`（每个 02 组件一份），确认 7.2.4 源代码文件清单、8.2 软件单元与函数设计齐全，函数 ID 与 9 可追溯性能对上。
4. 读 `04-implementation.md` 的任务卡，确认每条 SSR 都被任务覆盖，且「验证 / 证据」可复跑。
5. 人按 `01-requirements.md` 的需求卡逐条验收，抽查 `04-implementation.md` 的证据。

## 验证

在技能根目录运行：

```bash
python scripts/check_requirements.py    examples/todo-cli/SDD/01-requirements.md
python scripts/check_architecture.py    examples/todo-cli/SDD
python scripts/check_design.py          examples/todo-cli/SDD
python scripts/check_implementation.py  examples/todo-cli/SDD/04-implementation.md
python scripts/check_chain.py           examples/todo-cli/SDD
```

五道检查应当全部通过（0 错误 0 警告）。

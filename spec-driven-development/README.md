# spec-driven-development

以规范驱动开发（SDD）流程约束软件变更的教学样例：先写变更规格、经确认后拆解任务，再逐步实施与验收。

## 安装

1. 将 `spec-driven-development/` 目录复制到你的 skills 目录
2. 无额外依赖（脚本仅使用 Python 标准库）

## 使用方法

对 Agent 说"帮我修改 xxx，走 SDD 流程"，Agent 会：

1. 创建 `specs/<变更名>/spec.md` 并按模板填写
2. 运行 `python scripts/check_spec.py specs/<变更名>/spec.md` 做规格门禁
3. 向你呈现规格摘要，等待你确认
4. 拆解任务清单到 `tasks.md`，逐任务实施与验证
5. 对照验收标准逐条核对，更新 README/CHANGELOG

## 输出格式

- `specs/<变更名>/spec.md`：变更规格
- `specs/<变更名>/tasks.md`：带验证步骤的任务清单
- 验收结论：每条验收标准的通过情况

完整流程示例见 `examples/change-flow.md`。

## 目录结构

```text
spec-driven-development/
├── SKILL.md                    # 核心执行文件
├── metadata.json               # 元信息
├── examples/change-flow.md     # 完整变更流程示例
├── scripts/check_spec.py       # 规格文档校验脚本
├── resources/                  # 规格模板与流程配置
│   ├── prompt.md
│   └── config.yaml
├── tests/                      # 测试用例
│   ├── test_cases.md
│   └── eval.yaml
├── README.md
└── CHANGELOG.md
```
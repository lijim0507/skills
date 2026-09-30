# skill-demo

参照菜鸟教程《Skills 基本结构》与《Skills 目录结构》编写的教学样例：分析 PDF 并生成 Markdown 摘要。

## 安装

1. 将 `skill-demo/` 目录复制到你的 skills 目录
2. 安装脚本依赖：`pip install pypdf`

## 使用方法

对 Agent 说"帮我分析 xxx.pdf 并总结"，或在手动模式下执行：

```bash
python scripts/extract.py <PDF路径> [--start-page N] [--max-pages N]
```

## 输出格式

Markdown 摘要，包含 `核心内容` 与 `关键要点` 两个部分，见 `examples/summary.md`。

## 目录结构

```text
skill-demo/
├── SKILL.md              # 核心执行文件
├── metadata.json         # 元信息
├── examples/summary.md   # 输入输出示例
├── scripts/extract.py    # PDF 文本提取脚本
├── resources/            # 提示词模板与配置
│   ├── prompt.md
│   └── config.yaml
├── tests/                # 测试用例
│   ├── test_cases.md
│   └── eval.yaml
├── README.md
└── CHANGELOG.md
```
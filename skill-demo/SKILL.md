---
name: skill-demo
description: 分析 PDF 文件并生成结构化 Markdown 摘要。当用户需要提取 PDF 文本、总结文档内容，或提到 PDF、文档摘要、文档分析时使用；不适用于图片编辑或视频处理。
license: Apache-2.0
metadata:
  author: lijingyuan
  version: "1.0.0"
  tags:
    - pdf
    - document
    - summary
---

# PDF 分析 Skill

## Description

读取 PDF 文件，提取文本内容，并生成结构化的 Markdown 摘要。

## When to use

适用于：

- 提取 PDF 文本内容
- 生成文档摘要
- 分析 PDF 章节结构

## When NOT to use

不适用于：

- 图片编辑
- 视频处理
- Word、Excel 等其他格式的文档转换

## Input

从对话上下文中获取以下信息：

- **文件路径**（必填）：PDF 文件路径
- **分析目标**（可选）：用户希望了解什么，如"总结全文"、"提取关键数据"
- **输出语言**（可选）：默认读取 `resources/config.yaml` 中的 `language` 配置

若文件路径未明确，先向用户确认后再执行。

## Instructions

1. 校验输入：确认文件存在、扩展名为 `.pdf`；文件超过 100 MB 时提醒用户处理可能较慢
2. 提取文本：运行以下命令并读取输出

   ```bash
   python scripts/extract.py <PDF路径> [--start-page N] [--max-pages N]
   ```

3. 识别章节结构：根据标题与段落分布划分章节
4. 生成摘要：按 `resources/prompt.md` 的模板组织内容，长度与语言遵循 `resources/config.yaml`
5. 输出结果：以 Markdown 格式返回，并在开头注明分析的文件名与页数

脚本依赖 `pypdf`。未安装时提示用户执行 `pip install pypdf`。

## Output

返回 Markdown 格式摘要，结构如下：

```markdown
# 文档摘要：<文件名>

## 核心内容
1. …
2. …
3. …

## 关键要点
- …
```
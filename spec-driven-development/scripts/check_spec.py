"""校验 SDD 变更规格文档是否符合规范。"""

import argparse
import os
import re
import sys

REQUIRED_SECTIONS = ("背景", "目标", "范围", "非目标", "影响面", "验收标准")
MAX_LINES = 200


def validate_spec(file_path):
    """校验规格文件，返回 (是否通过, 问题列表)。"""
    if not file_path:
        return False, ["错误：未提供规格文件路径"]
    if not os.path.exists(file_path):
        return False, [f"错误：规格文件不存在 → {file_path}"]
    if not file_path.lower().endswith(".md"):
        return False, ["错误：规格文件必须是 .md 格式"]

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    if not content.strip():
        return False, ["错误：规格文件为空"]

    issues = []
    for section in REQUIRED_SECTIONS:
        pattern = r"^##\s+" + section + r"\s*$"
        if not re.search(pattern, content, re.MULTILINE):
            issues.append(f"错误：缺少必需章节「{section}」")

    match = re.search(r"^##\s+验收标准\s*$(.*?)(?=^##\s|\Z)", content, re.MULTILINE | re.DOTALL)
    if match and not re.search(r"^\s*(?:[-*]|\d+\.)\s+", match.group(1), re.MULTILINE):
        issues.append("错误：「验收标准」章节下没有逐条列出的可核对条目")

    if len(content.splitlines()) > MAX_LINES:
        issues.append(f"警告：规格超过 {MAX_LINES} 行，建议拆分为多个变更")

    has_error = any(issue.startswith("错误") for issue in issues)
    return not has_error, issues


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    parser = argparse.ArgumentParser(description="SDD 规格文档校验脚本")
    parser.add_argument("file", help="必填：spec.md 文件路径")
    args = parser.parse_args()

    ok, issues = validate_spec(args.file)
    for issue in issues:
        print(issue)
    if ok:
        print("规格校验通过")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
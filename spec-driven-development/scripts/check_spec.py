"""校验 SDD 规格文档（01-spec.md）是否符合规范。"""

import argparse
import os
import re
import sys

REQUIRED_SECTIONS = ("用户场景与测试", "需求", "成功标准")
IMPL_LEAK = re.compile(r"\bGPIO\s*\d+|\bIO\s*\d+|\bTMR\s*\d+|\buint\d+_t\b", re.IGNORECASE)


def validate_spec(file_path):
    """返回 (是否通过, 问题列表)。"""
    if not file_path:
        return False, ["错误：未提供规格文件路径"]
    if not os.path.exists(file_path):
        return False, [f"错误：规格文件不存在 → {file_path}"]
    if not file_path.lower().endswith(".md"):
        return False, ["错误：规格文件必须是 .md 格式"]

    with open(file_path, "r", encoding="utf-8") as handle:
        content = handle.read()

    if not content.strip():
        return False, ["错误：规格文件为空"]

    issues = []
    for section in REQUIRED_SECTIONS:
        if not re.search(r"^##\s+" + re.escape(section), content, re.MULTILINE):
            issues.append(f"错误：缺少必需章节「{section}」")

    stories = re.findall(r"^###\s+用户故事[^\n]*$", content, re.MULTILINE)
    if not stories:
        issues.append("错误：没有任何用户故事")

    scenes = re.findall(r"\*\*验收场景\*\*", content)
    if stories and len(scenes) < len(stories):
        issues.append(f"错误：{len(stories)} 个用户故事只有 {len(scenes)} 个「验收场景」")
        issues.append("提示：验收场景是落点判定的锚点，每个故事都必须有")

    if not re.search(r"\bSC-\d+", content):
        issues.append("错误：「成功标准」下没有可测量的条目（SC-xxx）")

    leaks = IMPL_LEAK.findall(content)
    if leaks:
        sample = "、".join(sorted(set(leaks))[:5])
        issues.append(f"警告：spec 里出现实现细节（{sample}）")
        issues.append("提示：问一句「删掉它，验收还做得成吗」，做得成即应搬去 02-plan.md")

    open_items = re.findall(r"\[NEEDS CLARIFICATION", content)
    if open_items:
        issues.append(f"提示：仍有 {len(open_items)} 处 [NEEDS CLARIFICATION] 未闭合")

    has_error = any(item.startswith("错误") for item in issues)
    return not has_error, issues


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    parser = argparse.ArgumentParser(description="SDD 规格文档校验")
    parser.add_argument("file", help="必填：01-spec.md 路径")
    args = parser.parse_args()

    ok, issues = validate_spec(args.file)
    for issue in issues:
        print(issue)
    if ok:
        print("规格校验通过")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
"""校验 SDD 任务文档的状态标记与追溯。"""

import argparse
import os
import re
import sys

TASK_RE = re.compile(r"^-\s+\[( |x|~)\]\s+(T\d+)(.*)$")
STRIKE_RE = re.compile(r"~~.+~~")
REPLACED_RE = re.compile(r"^\s*⤷")
TRACE_RE = re.compile(r"(plan\s*[:：]|FR-|流程)")


def validate_tasks(file_path):
    """返回 (是否通过, 问题列表, 统计)。"""
    if not file_path:
        return False, ["错误：未提供任务文件路径"], {}
    if not os.path.exists(file_path):
        return False, [f"错误：任务文件不存在 → {file_path}"], {}

    with open(file_path, "r", encoding="utf-8") as handle:
        lines = handle.read().splitlines()

    issues = []
    counts = {" ": 0, "x": 0, "~": 0}

    for index, line in enumerate(lines):
        match = TASK_RE.match(line)
        if not match:
            continue
        status, task_id, rest = match.group(1), match.group(2), match.group(3)
        counts[status] += 1

        if status == "~":
            if not STRIKE_RE.search(rest):
                issues.append(f"错误：{task_id} 已作废但内容没有删除线")
                issues.append("提示：作废任务的格式是 [~] ~~原描述~~ ，任务号留在删除线外")
            following = lines[index + 1] if index + 1 < len(lines) else ""
            if not REPLACED_RE.match(following):
                issues.append(f"错误：{task_id} 已作废但下一行缺少 ⤷ 说明（被谁取代、为什么）")
        elif not TRACE_RE.search(rest):
            issues.append(f"警告：{task_id} 没有 plan 落点或 FR 编号，analyze 会报追溯缺失")

    pending = counts[" "]
    done = counts["x"]
    voided = counts["~"]

    has_error = any(item.startswith("错误") for item in issues)
    return not has_error, issues, (pending, done, voided)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    parser = argparse.ArgumentParser(description="SDD 任务状态校验")
    parser.add_argument("file", help="必填：03-tasks.md 路径")
    args = parser.parse_args()

    ok, issues, counts = validate_tasks(args.file)
    for issue in issues:
        print(issue)
    pending, done, voided = counts if counts else (0, 0, 0)
    print(f"任务统计：未完成 {pending} ｜ 已完成 {done} ｜ 已作废 {voided}")
    if ok:
        print("任务状态校验通过")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
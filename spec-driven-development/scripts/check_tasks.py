"""校验 SDD 任务行的状态标记与追溯。

退出码 0 = 无「错误」（警告与提示不阻断）。

用法：python check_tasks.py <03-tasks.md>
"""

import argparse
import os
import re
import sys

TASK_RE = re.compile(r"^\s*[-*]\s+\[([ x~])\]\s+(.*)$")
LEADING_ID_RE = re.compile(r"^T\d+")
ANY_ID_RE = re.compile(r"T\d+")
STRIKE_SPAN_RE = re.compile(r"~~.*?~~")
REPLACED_RE = re.compile(r"^\s*⤷")
TRACE_RE = re.compile(r"(plan\s*[:：]|FR-|流程)")

FENCE_MARK = chr(0x60) * 3
FENCE_RE = re.compile(r"^\s*(?:" + FENCE_MARK + r"|~~~)")


def visible_lines(content):
    kept = []
    in_fence = False
    for line in content.splitlines():
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence:
            kept.append(line)
    return kept


def validate_tasks(file_path):
    """返回 (是否通过, 问题列表, (未完成, 已完成, 已作废))。"""
    if not file_path:
        return False, ["错误：未提供任务文件路径"], (0, 0, 0)
    if not os.path.exists(file_path):
        return False, ["错误：任务文件不存在 → " + file_path], (0, 0, 0)

    with open(file_path, "r", encoding="utf-8") as handle:
        lines = visible_lines(handle.read())

    issues = []
    counts = {" ": 0, "x": 0, "~": 0}

    for index, line in enumerate(lines):
        match = TASK_RE.match(line)
        if not match:
            continue
        status, payload = match.group(1), match.group(2).strip()
        counts[status] += 1

        leading = LEADING_ID_RE.match(payload)
        if leading:
            task_id = leading.group(0)
        else:
            found = ANY_ID_RE.search(payload)
            if found:
                task_id = found.group(0)
                issues.append(
                    "错误：" + task_id + " 的任务号没有紧跟状态（被划入删除线或加了前缀）"
                    "——任务号必须留在删除线外，否则统计与检索都会失真"
                )
            else:
                issues.append("警告：第 " + str(index + 1) + " 行是任务行但没有任务号 T 加数字，未计入统计")
                continue

        spans = STRIKE_SPAN_RE.findall(payload)
        if status == "~":
            if not spans:
                issues.append("错误：" + task_id + " 已作废但内容没有删除线")
                issues.append("提示：作废任务的格式是 [~] 加一对波浪线包住原描述，任务号留在删除线外")
            elif any(task_id in span for span in spans):
                issues.append("错误：" + task_id + " 的任务号被划进了删除线，应留在删除线外（保持可检索）")
            following = ""
            for later in lines[index + 1:]:
                if later.strip():
                    following = later
                    break
            if not REPLACED_RE.match(following):
                issues.append("错误：" + task_id + " 已作废但缺少 ⤷ 说明（被谁取代、为什么）")
        elif not TRACE_RE.search(payload):
            issues.append("警告：" + task_id + " 没有 plan 落点或 FR 编号，analyze 会报追溯缺失")

    pending, done, voided = counts[" "], counts["x"], counts["~"]
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
    pending, done, voided = counts
    print("任务统计：未完成 " + str(pending) + " ｜ 已完成 " + str(done) + " ｜ 已作废 " + str(voided))
    if ok:
        print("任务状态校验通过")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

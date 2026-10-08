"""校验变更轮受理单的自洽性：落点 与 重走范围。"""

import argparse
import os
import re
import sys

GATE1 = "门 1"
GATE2 = "门 2"

# 落点 -> (必须出现, 不得出现)
EXPECTED = {
    "spec": ([GATE1, GATE2], []),
    "plan": ([GATE2], [GATE1]),
    "tasks": ([], [GATE1, GATE2]),
    "仅实现": ([], [GATE1, GATE2]),
}

FIELD_RE = re.compile(r"^>\s*-\s*\*\*(落点|重走范围|判定依据|处置记录)\*\*[:：]\s*(.*)$")
LEGACY_SCOPE_RE = re.compile(r"^>\s*-\s*\*\*同时触及\*\*")
ROUND_RE = re.compile(r"^#{2,3}\s+变更轮")
REQUIRED_FIELDS = ("落点", "重走范围", "判定依据")


def parse_intakes(content):
    """收集所有变更轮的受理单，返回 [(小节标题, 字段字典, 是否单开了「同时触及」栏)]。"""
    found = []
    title = None
    fields = {}
    legacy_scope = False
    for line in content.splitlines():
        if ROUND_RE.match(line):
            if title is not None:
                found.append((title, fields, legacy_scope))
            title = line.strip()
            fields = {}
            legacy_scope = False
            continue
        if title is None:
            continue
        stripped = line.strip()
        if LEGACY_SCOPE_RE.match(stripped):
            legacy_scope = True
            continue
        match = FIELD_RE.match(stripped)
        if match:
            fields[match.group(1)] = match.group(2).strip()
    if title is not None:
        found.append((title, fields, legacy_scope))
    return found


def classify(landing_value):
    """从「spec（最高处）」这样的值里取出基础落点。"""
    if not landing_value:
        return None
    for key in EXPECTED:
        if landing_value.startswith(key):
            return key
    return None


def validate_intake(file_path):
    if not file_path:
        return False, ["错误：未提供任务文件路径"]
    if not os.path.exists(file_path):
        return False, [f"错误：任务文件不存在 → {file_path}"]

    with open(file_path, "r", encoding="utf-8") as handle:
        content = handle.read()

    if not content.strip():
        return False, ["错误：任务文件为空"]

    issues = []
    rounds = parse_intakes(content)
    if not rounds:
        issues.append("提示：没有找到任何变更轮小节（首轮建档时正常）")
        return True, issues

    for title, fields, legacy_scope in rounds:
        if legacy_scope:
            issues.append(f"错误：{title} 的「同时触及」应并入落点行，不单独成栏")
        missing = [name for name in REQUIRED_FIELDS if not fields.get(name)]
        if missing:
            missing_text = "、".join(missing)
            issues.append(f"错误：{title} 的受理单缺少 {missing_text}")
            continue

        landing = classify(fields["落点"])
        if landing is None:
            value = fields["落点"]
            issues.append(f"错误：{title} 的落点值无法识别：{value}")
            continue

        scope = fields["重走范围"]
        must, must_not = EXPECTED[landing]
        for gate in must:
            if gate not in scope:
                issues.append(f"错误：{title} 落点为 {landing}，重走范围却未包含 {gate}")
        for gate in must_not:
            if gate in scope:
                issues.append(f"错误：{title} 落点为 {landing}，重走范围不应包含 {gate}")

    has_error = any(item.startswith("错误") for item in issues)
    return not has_error, issues


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    parser = argparse.ArgumentParser(description="SDD 受理单自洽校验")
    parser.add_argument("file", help="必填：03-tasks.md 路径")
    args = parser.parse_args()

    ok, issues = validate_intake(args.file)
    for issue in issues:
        print(issue)
    if ok:
        print("受理单校验通过")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
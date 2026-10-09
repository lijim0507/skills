"""校验变更轮受理单：五栏齐全，落点 ↔ 重走范围 ↔ 验收场景 自洽。

只查自洽，不查「落点判得对不对」——那要靠人，以及与 git diff 对照的 check_landing.py。

用法：python check_intake.py <03-tasks.md>
"""

import argparse
import os
import re
import sys

# 落点 -> (重走范围必须包含, 不得包含)；门名先归一化去空白，比较用 门1 / 门2
EXPECTED = {
    "宪法": (["门1", "门2"], []),
    "spec": (["门1", "门2"], []),
    "澄清": (["门1"], ["门2"]),
    "plan": (["门2"], ["门1"]),
    "tasks": ([], ["门1", "门2"]),
    "仅实现": ([], ["门1", "门2"]),
}

LANDING_KEYS = (
    ("澄清", "澄清"),
    ("宪法", "宪法"),
    ("constitution", "宪法"),
    ("spec", "spec"),
    ("plan", "plan"),
    ("tasks", "tasks"),
    ("仅实现", "仅实现"),
)

FIELD_RE = re.compile(r"^>\s*-\s*\*\*(落点|验收场景|重走范围|判定依据|处置记录)\*\*[:：]\s*(.*)$")
LEGACY_SCOPE_RE = re.compile(r"^>\s*-\s*\*\*同时触及\*\*")
ROUND_RE = re.compile(r"^#{2,3}\s+(?:r\d+\s+)?变更轮(?:$|[\s（(【:：·—-])")

FENCE_MARK = chr(0x60) * 3
FENCE_RE = re.compile(r"^\s*(?:" + FENCE_MARK + r"|~~~)")

REQUIRED_FIELDS = ("落点", "验收场景", "重走范围", "判定依据", "处置记录")
SCENE_CHANGED = "有变化"
SCENE_UNCHANGED = "无变化"
DOWNSTREAM_LANDINGS = ("plan", "tasks", "仅实现")
CLARIFY_LANDING = "澄清"


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


def parse_intakes(content):
    """返回 [(小节标题, 字段字典, 是否单开了「同时触及」栏)]。"""
    found = []
    title = None
    fields = {}
    legacy_scope = False
    for line in visible_lines(content):
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
    if not landing_value:
        return None
    lowered = landing_value.strip().lower()
    for key, landing in LANDING_KEYS:
        if lowered.startswith(key):
            return landing
    return None


def normalize(text):
    return re.sub(r"\s+", "", text or "")


def validate_intake(file_path):
    if not file_path:
        return False, ["错误：未提供任务文件路径"]
    if not os.path.exists(file_path):
        return False, ["错误：任务文件不存在 → " + file_path]

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
            issues.append("错误：" + title + " 的「同时触及」应并入落点行，不单独成栏")

        missing = [name for name in REQUIRED_FIELDS if not fields.get(name)]
        if missing:
            issues.append("错误：" + title + " 的受理单缺少 " + "、".join(missing))
            continue

        landing = classify(fields["落点"])
        if landing is None:
            issues.append("错误：" + title + " 的落点值无法识别：" + fields["落点"])
            continue

        scope = normalize(fields["重走范围"])
        must, must_not = EXPECTED[landing]
        for gate in must:
            if gate not in scope:
                issues.append("错误：" + title + " 落点为 " + landing + "，重走范围却未包含 门 " + gate[-1])
        for gate in must_not:
            if gate in scope:
                issues.append("错误：" + title + " 落点为 " + landing + "，重走范围不应包含 门 " + gate[-1])

        scene = normalize(fields["验收场景"])
        if SCENE_CHANGED in scene:
            if landing in DOWNSTREAM_LANDINGS:
                issues.append(
                    "错误：" + title + " 的验收场景写了「有变化」，落点却是 " + landing
                    + "——验收场景变了就是 spec 落点（判不准按上游）"
                )
            elif landing == CLARIFY_LANDING:
                issues.append(
                    "错误：" + title + " 的落点是「澄清」却写了「有变化」——"
                    "澄清的定义就是验收场景不变；场景真变了请把落点改成 spec"
                )
        elif SCENE_UNCHANGED in scene:
            if landing in ("spec", "宪法"):
                issues.append(
                    "提示：" + title + " 落点为 " + landing + " 但验收场景写「无变化」"
                    "——若只是澄清而非需求变更，请确认；否则核对是否该按上游处理"
                )
        else:
            issues.append(
                "错误：" + title + " 的「验收场景」栏只能填「有变化」或「无变化」，当前为：" + fields["验收场景"]
            )

        if landing == CLARIFY_LANDING:
            scope_text = fields["重走范围"]
            if "analyze" not in normalize(scope_text):
                issues.append(
                    "提示：" + title + " 的落点是「澄清」，重走范围建议含 analyze"
                    "——文字澄清最容易改出语义，让 analyze 复核一次文档间一致性"
                )

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

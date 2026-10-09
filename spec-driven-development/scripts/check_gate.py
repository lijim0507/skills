"""校验评审门是否留下「人批准」的记录。

能拦住的是「待审 / reject / 占位符 / 缺裁决人与日期」这类机械问题；
**署名的真实性脚本查不出来**——裁决人是不是真的那个人，只能靠人自己守。

记录位置（一条规则，两处落点）：
- 首轮：结论写在被审文档的门小节里——01-spec.md 的门 1、02-plan.md 的门 2
- 变更轮：结论写在 03-tasks.md 的受理单里——受理单就是这个变更轮的人审材料

用法：
  python check_gate.py <03-tasks.md>
  python check_gate.py <03-tasks.md> --spec <01-spec.md> --plan <02-plan.md>
  python check_gate.py --spec <01-spec.md> --plan <02-plan.md>
"""

import argparse
import os
import re
import sys

ROUND_RE = re.compile(r"^#{2,3}\s+(?:r\d+\s+)?变更轮(?:$|[\s（(【:：·—-])")
SCOPE_FIELD_RE = re.compile(r"^>\s*-\s*\*\*重走范围\*\*[:：]\s*(.*)$")
GATE_FIELD_RE = re.compile(r"^>\s*-\s*\*\*门\s*([12])\*\*[:：]\s*(.*)$")
GATE_IN_SCOPE_RE = re.compile(r"门\s*([12])")
GATE_SECTION_RE = re.compile(r"^#{2,3}\s*(?:评审)?门\s*([12])(?:\s|$|[（(·—-])")
HEADING_RE = re.compile(r"^#{1,6}\s")

FENCE_MARK = chr(0x60) * 3
FENCE_RE = re.compile(r"^\s*(?:" + FENCE_MARK + r"|~~~)")

VERDICTS = (
    ("reject", ("reject", "驳回", "拒绝")),
    ("approve", ("approve", "批准", "通过", "同意")),
    ("pending", ("待审", "待批", "待定", "pending")),
)
PLACEHOLDER_RE = re.compile(r"^<.*>$")


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


def find_verdict(text):
    """只看第一个「｜」之前的那一段，取其中**最早**出现的判定词。

    这样「approve（上一轮 reject 已修复）」判成 approve，
    而不会因为句中提到 reject 就被误判成驳回。
    """
    segment = re.split(r"[｜|]", text or "", maxsplit=1)[0].lower()
    best = None
    for name, keys in VERDICTS:
        for key in keys:
            position = segment.find(key)
            if position >= 0 and (best is None or position < best[0]):
                best = (position, name)
    return best[1] if best else None


def extract_value(text, names):
    for name in names:
        match = re.search(name + r"\s*[:：]\s*([^｜|\n]*)", text or "")
        if match:
            value = match.group(1).strip()
            if value and not PLACEHOLDER_RE.match(value):
                return value
    return None


def check_record(where, gate, verdict_text, meta_text, issues):
    """校验单条门记录：必须已批准，且带裁决人与日期。"""
    verdict = find_verdict(verdict_text)
    if verdict is None:
        issues.append("错误：" + where + " 的门 " + gate + " 没有可识别的结论（approve / reject / 待审）")
        return
    if verdict == "pending":
        issues.append("错误：" + where + " 的门 " + gate + " 仍是「待审」——未获批准不得进入下一步")
        return
    if verdict == "reject":
        issues.append("错误：" + where + " 的门 " + gate + " 为 reject——必须退回上游修，修完重跑该门，不得带病继续")
        return
    if not extract_value(meta_text, ("裁决人", "评审人", "批准人")):
        issues.append("错误：" + where + " 的门 " + gate + " 缺「裁决人」（未填或仍是占位符）——门必须由人批")
    if not extract_value(meta_text, ("日期", "批准日期")):
        issues.append("错误：" + where + " 的门 " + gate + " 缺「日期」（未填或仍是占位符）")


def check_rounds(content):
    """变更轮：重走范围里经过的门，必须有对应的已批准记录。"""
    issues = []
    rounds = []
    title = None
    scope = ""
    records = {}

    def flush():
        if title is not None:
            rounds.append((title, scope, dict(records)))

    for line in visible_lines(content):
        if ROUND_RE.match(line):
            flush()
            title = line.strip()
            scope = ""
            records = {}
            continue
        if title is None:
            continue
        stripped = line.strip()
        match = SCOPE_FIELD_RE.match(stripped)
        if match:
            scope = match.group(1)
            continue
        match = GATE_FIELD_RE.match(stripped)
        if match:
            records[match.group(1)] = match.group(2)
    flush()

    for round_title, scope, records in rounds:
        required = sorted(set(GATE_IN_SCOPE_RE.findall(scope)))
        for gate in required:
            if gate not in records:
                issues.append(
                    "错误：" + round_title + " 的重走范围含门 " + gate + "，却缺门 " + gate
                    + " 的结论记录（格式：> - **门 " + gate + "**：approve ｜ 裁决人：… ｜ 日期：…）"
                )
        for gate, text in sorted(records.items()):
            check_record(round_title, gate, text, text, issues)

    if not rounds:
        issues.append("提示：没有找到变更轮小节（首轮建档时正常）")
    return issues


def check_gate_sections(path, issues):
    """首轮：结论写在被审文档的门小节里。"""
    if not path:
        return
    if not os.path.exists(path):
        issues.append("错误：文件不存在 → " + path)
        return

    where = os.path.basename(path)
    with open(path, "r", encoding="utf-8") as handle:
        lines = visible_lines(handle.read())

    gate = None
    verdict_text = None
    section = []
    found = set()

    def flush():
        if gate is None or verdict_text is None:
            return
        meta = verdict_text + " " + " ".join(section)
        check_record(where, gate, verdict_text, meta, issues)
        found.add(gate)

    for line in lines:
        if HEADING_RE.match(line):
            flush()
            match = GATE_SECTION_RE.match(line)
            gate = match.group(1) if match else None
            verdict_text = None
            section = []
            continue
        if gate is None:
            continue
        if line.startswith("**结论**") and verdict_text is None:
            verdict_text = re.sub(r"^\*\*结论\*\*\s*[:：]?", "", line).strip()
            continue
        if verdict_text is not None:
            section.append(line)
    flush()

    if not found:
        issues.append("提示：" + where + " 里没有找到可校验的「门 N → 结论」记录")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    parser = argparse.ArgumentParser(description="SDD 评审门批准记录校验")
    parser.add_argument("file", nargs="?", help="03-tasks.md 路径（校验变更轮的门结论）")
    parser.add_argument("--spec", help="01-spec.md 路径（校验门 1）")
    parser.add_argument("--plan", help="02-plan.md 路径（校验门 2）")
    args = parser.parse_args()
    if not args.file and not args.spec and not args.plan:
        parser.error("至少要给一个文件：03-tasks.md 或 --spec / --plan")

    issues = []
    if args.file:
        if not os.path.exists(args.file):
            issues.append("错误：任务文件不存在 → " + args.file)
        else:
            with open(args.file, "r", encoding="utf-8") as handle:
                issues += check_rounds(handle.read())
    check_gate_sections(args.spec, issues)
    check_gate_sections(args.plan, issues)

    has_error = any(item.startswith("错误") for item in issues)
    for issue in issues:
        print(issue)
    if not has_error:
        print("门记录校验通过")
    sys.exit(1 if has_error else 0)


if __name__ == "__main__":
    main()

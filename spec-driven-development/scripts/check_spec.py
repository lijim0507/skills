"""校验 SDD 规格文档（01-spec.md）的结构。

只做结构检查，不替人判断；退出码 0 = 无「错误」（警告与提示不阻断）。
「前提假设」节与带 <!-- impl-ok --> 的行不参与实现细节检查——外部给定的硬约束
本来就允许含具体值（判据见 references/doc-set.md）。

用法：python check_spec.py <01-spec.md>
"""

import argparse
import os
import re
import sys

# 章节名容错：「## 功能需求」也算「需求」
SECTION_PATTERNS = (
    ("用户场景与测试", r"^##\s+(?:用户场景与测试|用户场景|场景与测试)"),
    ("需求", r"^##\s+(?:功能)?需求"),
    ("成功标准", r"^##\s+成功标准"),
)

# 实现细节符号：判据见 references/doc-set.md 的「反向检验」一节
IMPL_LEAK = re.compile(
    r"\b(?:GPIO|IO|PA|PB|PC|PD|PE|PF|PG)\s?\d+"
    r"|\b(?:TMR|TIM|ADC|SPI|I2C|I2S|UART|USART|DMA)\d*\b"
    r"|\b(?:uint|int|bool|char|float|double)\d*_t\b"
    r"|0x[0-9A-Fa-f]{2,}"
    r"|引脚|外设通道|时钟树|中断优先级|寄存器|波特率|结构体|函数签名",
    re.IGNORECASE,
)

FENCE_MARK = chr(0x60) * 3
FENCE_RE = re.compile(r"^\s*(?:" + FENCE_MARK + r"|~~~)")
CHECKBOX_RE = re.compile(r"^\s*[-*]\s+\[[ x~]\]")
GATE1_RE = re.compile(r"^##\s+门\s*1")
SECTION_HEAD_RE = re.compile(r"^#{2,4}\s+(.*)$")
STORY_HEAD_RE = re.compile(r"^###\s+用户故事")
EXEMPT_SECTIONS = ("前提假设", "Assumptions")
IMPL_OK_MARK = "<!-- impl-ok -->"
SCENE_MARK = "**验收场景**"


def visible_lines(content):
    """去掉代码围栏，返回 [(行号, 行内容)]。"""
    kept = []
    in_fence = False
    for number, line in enumerate(content.splitlines(), start=1):
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence:
            kept.append((number, line))
    return kept


def stories_missing_scenes(lines):
    """按用户故事分段，返回缺少「验收场景」的故事标题。"""
    missing = []
    state = {"title": None, "has_scene": False}

    def close():
        if state["title"] is not None and not state["has_scene"]:
            missing.append(state["title"])

    for _, text in lines:
        story = STORY_HEAD_RE.match(text)
        if story:
            close()
            state["title"] = text[story.end():].strip() or "（未命名）"
            state["has_scene"] = False
            continue
        if state["title"] is None:
            continue
        if re.match(r"^#{1,3}\s", text):
            close()
            state["title"] = None
            continue
        if SCENE_MARK in text:
            state["has_scene"] = True
    close()
    return missing


def in_exempt_section(section):
    return any(section.startswith(name) for name in EXEMPT_SECTIONS)


def validate_spec(file_path):
    """返回 (是否通过, 问题列表)。"""
    if not file_path:
        return False, ["错误：未提供规格文件路径"]
    if not os.path.exists(file_path):
        return False, ["错误：规格文件不存在 → " + file_path]
    if not file_path.lower().endswith(".md"):
        return False, ["错误：规格文件必须是 .md 格式"]

    with open(file_path, "r", encoding="utf-8") as handle:
        content = handle.read()

    if not content.strip():
        return False, ["错误：规格文件为空"]

    lines = visible_lines(content)
    body = "\n".join(text for _, text in lines)
    issues = []

    for section, pattern in SECTION_PATTERNS:
        if not re.search(pattern, body, re.MULTILINE):
            issues.append("错误：缺少必需章节「" + section + "」")

    stories = re.findall(r"^###\s+用户故事[^\n]*$", body, re.MULTILINE)
    if not stories:
        issues.append("错误：没有任何用户故事")

    scenes = re.findall(r"\*\*验收场景\*\*", body)
    if stories and len(scenes) < len(stories):
        issues.append("错误：" + str(len(stories)) + " 个用户故事只有 " + str(len(scenes)) + " 个「验收场景」")
        issues.append("提示：验收场景是判据的锚点，每个用户故事都必须有")

    missing_stories = stories_missing_scenes(lines)
    if missing_stories:
        issues.append("错误：这些用户故事名下没有「验收场景」：" + "、".join(missing_stories))
        issues.append("提示：验收场景必须写在对应故事的小节内，写在别的故事里不算数")

    if not re.search(r"\bSC-\d+", body):
        issues.append("错误：「成功标准」下没有可测量的条目（SC-xxx）")

    leaks = []
    section = ""
    for _, text in lines:
        head = SECTION_HEAD_RE.match(text)
        if head:
            section = head.group(1).strip()
        if text.lstrip().startswith(">") or CHECKBOX_RE.match(text):
            continue  # 注记行与门 1 清单行本来就在讲这条判据
        if in_exempt_section(section) or IMPL_OK_MARK in text:
            continue  # 前提假设节 / 显式豁免行：硬约束本来就可以含具体值
        leaks.extend(IMPL_LEAK.findall(text))
    if leaks:
        sample = "、".join(sorted(set(leaks))[:5])
        issues.append("警告：spec 里出现实现细节（" + sample + "）")
        issues.append("提示：问一句「删掉它，验收还做得成吗」，做得成即应搬去 02-plan.md")
        issues.append("提示：外部给定的硬约束请写进「前提假设」节，或在该行加 <!-- impl-ok --> 标记")

    gate = GATE1_RE.search(body)
    if gate:
        tail = body[gate.end():]
        verdict = re.search(r"\*\*结论\*\*[:：]\s*(.*)", tail)
        if not verdict:
            # 只查「有没有结论行」；结论的语义（是否真的批了）由 check_gate.py 负责
            issues.append("警告：门 1 小节缺少「结论」行（approve / reject / 待审）")

    open_items = []
    for _, text in lines:
        if text.lstrip().startswith(">") or CHECKBOX_RE.match(text):
            continue
        open_items.extend(re.findall(r"\[NEEDS CLARIFICATION", text))
    if open_items:
        issues.append("提示：仍有 " + str(len(open_items)) + " 处 [NEEDS CLARIFICATION] 未闭合")

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

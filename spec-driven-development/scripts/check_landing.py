"""把受理单的「验收场景」声明与 git diff 对照。

用法：python check_landing.py <01-spec.md> <03-tasks.md> [--since REF]

**什么时候跑**：改动**提交之前**跑，并用**变更前的基线**（--since <变更前的 commit/tag>）。
用默认的 HEAD 时，若改动已经提交，diff 会是空的，脚本只会给「无变化」提示——
安全网静默失效。

规则（只在能拿到基线时才有结论）：
- 01-spec.md 的验收场景相对 REF 有变化，而最新受理单没写「有变化」→ 错误
- 01-spec.md 的验收场景没有变化，而受理单写了「有变化」→ 提示
- 拿不到基线（不是 git 仓库 / ref 无效 / 文件不在仓库内）→ 提示，不阻断，但要求人工确认
"""

import argparse
import os
import re
import subprocess
import sys

STORY_RE = re.compile(r"^###\s+(用户故事.*)$")
SCENE_RE = re.compile(r"\*\*验收场景\*\*")
HEADING_RE = re.compile(r"^#{2,4}\s+")
ROUND_RE = re.compile(r"^#{2,3}\s+(?:r\d+\s+)?变更轮(?:$|[\s（(【:：·—-])")
LANDING_RE = re.compile(r"^>\s*-\s*\*\*落点\*\*[:：]\s*(.*)$")
SCENE_FIELD_RE = re.compile(r"^>\s*-\s*\*\*验收场景\*\*[:：]\s*(.*)$")

FENCE_MARK = chr(0x60) * 3
FENCE_RE = re.compile(r"^\s*(?:" + FENCE_MARK + r"|~~~)")

UPSTREAM_LANDINGS = ("宪法", "constitution", "spec")
SCENE_CHANGED = "有变化"
SCENE_UNCHANGED = "无变化"


def visible_lines(text):
    kept = []
    in_fence = False
    for line in text.splitlines():
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence:
            kept.append(line)
    return kept


def extract_scenes(text):
    """返回 {用户故事标题: 归一化后的验收场景全文}。"""
    scenes = {}
    story = None
    collecting = False
    buffer = []
    for line in visible_lines(text):
        story_match = STORY_RE.match(line)
        if story_match:
            if story and collecting:
                scenes[story] = "\n".join(buffer)
            story = story_match.group(1).strip()
            collecting = False
            buffer = []
            continue
        if story is None:
            continue
        if HEADING_RE.match(line):
            if collecting:
                scenes[story] = "\n".join(buffer)
            collecting = False
            buffer = []
            continue
        if SCENE_RE.search(line):
            collecting = True
            buffer = []
            continue
        if collecting:
            buffer.append(line.rstrip())
    if story and collecting:
        scenes[story] = "\n".join(buffer)
    return {key: re.sub(r"\s+", " ", value).strip() for key, value in scenes.items()}


def latest_intake(tasks_text):
    """取最后一个变更轮的 (落点, 验收场景栏)。"""
    landing = None
    scene = None
    for line in visible_lines(tasks_text):
        if ROUND_RE.match(line):
            landing = None
            scene = None
            continue
        stripped = line.strip()
        if landing is None:
            match = LANDING_RE.match(stripped)
            if match:
                landing = match.group(1).strip()
                continue
        if scene is None:
            match = SCENE_FIELD_RE.match(stripped)
            if match:
                scene = match.group(1).strip()
    return landing, scene


def run_git(args, cwd):
    try:
        return subprocess.run(
            ["git"] + args,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except (OSError, FileNotFoundError):
        return None


def read_baseline(spec_path, ref):
    """返回 (基线文本, None) 或 (None, 原因)。"""
    directory = os.path.dirname(os.path.abspath(spec_path)) or "."
    top = run_git(["rev-parse", "--show-toplevel"], directory)
    if top is None:
        return None, "找不到 git 命令"
    if top.returncode != 0:
        return None, "目标目录不是 git 仓库"
    prefix = run_git(["rev-parse", "--show-prefix"], directory)
    if prefix is None or prefix.returncode != 0:
        return None, "无法确定文件在仓库内的相对路径"
    relative = (prefix.stdout.strip() + os.path.basename(os.path.abspath(spec_path))).replace(os.sep, "/")
    show = run_git(["show", ref + ":" + relative], directory)
    if show.returncode != 0:
        return None, "git 取不到 " + ref + ":" + relative + "（未提交过 / 路径不在仓库内 / ref 无效）"
    return show.stdout, None


def validate_landing(spec_path, tasks_path, ref):
    issues = []
    if not spec_path or not os.path.exists(spec_path):
        return False, ["错误：规格文件不存在 → " + str(spec_path)]
    if not tasks_path or not os.path.exists(tasks_path):
        return False, ["错误：任务文件不存在 → " + str(tasks_path)]

    with open(spec_path, "r", encoding="utf-8") as handle:
        current = handle.read()
    with open(tasks_path, "r", encoding="utf-8") as handle:
        tasks_text = handle.read()

    baseline, reason = read_baseline(spec_path, ref)
    if baseline is None:
        issues.append(
            "提示：无法与 git 对照（" + str(reason) + "）——本次未做 diff 校验，"
            "请人工确认验收场景是否变化，并把结论写进受理单的「判定依据」栏"
        )
        return True, issues

    now = extract_scenes(current)
    before = extract_scenes(baseline)
    changed = sorted(key for key in set(now) | set(before) if now.get(key) != before.get(key))
    scene_changed = bool(changed)

    landing, scene_field = latest_intake(tasks_text)
    if landing is None or scene_field is None:
        issues.append("提示：没有找到同时带「落点」与「验收场景」的变更轮受理单，本次未做对照")
        return True, issues

    normalized = re.sub(r"\s+", "", scene_field)
    declared_changed = SCENE_CHANGED in normalized
    declared_unchanged = SCENE_UNCHANGED in normalized
    upstream = any(landing.strip().lower().startswith(key) for key in UPSTREAM_LANDINGS)

    if scene_changed and not declared_changed:
        issues.append(
            "错误：01-spec.md 的验收场景相对 " + ref + " 有变化（" + "、".join(changed) + "），"
            "但最新受理单落点是「" + landing + "」、验收场景栏是「" + scene_field + "」"
            "——验收场景变了就是 spec 落点，应重判并按 spec 重走（判不准按上游）"
        )
    elif declared_changed and not scene_changed:
        issues.append(
            "提示：受理单写「验收场景 有变化」，但 01-spec.md 相对 " + ref + " 的验收场景没有变化"
            "——若为澄清或新增需求，请确认；否则重判落点"
        )
    elif scene_changed:
        issues.append("提示：验收场景确实变了（" + "、".join(changed) + "），受理单声明一致")
    else:
        issues.append("提示：验收场景无变化，受理单声明一致")
        if upstream:
            issues.append("提示：落点为 " + landing + "，但 diff 未见验收场景变化——如属澄清，请在判定依据里写明")
        if ref.upper() == "HEAD":
            issues.append(
                "提示：本次基线是 HEAD（与工作区比较）。若改动已经提交，这里看到的是空 diff，"
                "请用变更前的 ref 重跑：--since <变更前的 commit/tag>"
            )

    has_error = any(item.startswith("错误") for item in issues)
    return not has_error, issues


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    parser = argparse.ArgumentParser(description="SDD 落点声明与 git diff 对照")
    parser.add_argument("spec", help="必填：01-spec.md 路径")
    parser.add_argument("tasks", help="必填：03-tasks.md 路径")
    parser.add_argument(
        "--since",
        default="HEAD",
        help="比对基线，默认 HEAD（与工作区比较）。改动已提交时必须显式传变更前的 commit/tag",
    )
    args = parser.parse_args()

    ok, issues = validate_landing(args.spec, args.tasks, args.since)
    for issue in issues:
        print(issue)
    if ok:
        print("落点对照通过（无阻断性不一致）")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

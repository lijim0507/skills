#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""架构检查（02-architecture.md，SWE.2 结构）。

只查机械事实：章节是否齐全、5.3 组件定义、组件名唯一、每个组件的「覆盖需求」、
动态行为整体时序图与阶段解释、追溯分析覆盖、文档头与章节顺序。
组件粒度好不好、分层是否合理由人确认前判断。

用法: python check_architecture.py <项目>/SDD
"""

import os
import re
import sys
import lint_common

FENCE = re.compile(r'^\s*(?:\x60\x60\x60|~~~)')
SSR_ID = r'SSR\d{3,}'
REQ_ID = r'REQ(?:-[A-Za-z0-9]+)+'
ANY_ID = re.compile(r'\b(' + SSR_ID + r'|' + REQ_ID + r')\b')

LAYERS = ('5.3.4', '5.3.5', '5.3.6')


def read_unfenced(path):
    with open(path, encoding='utf-8') as fh:
        raw = fh.read().splitlines()
    out = []
    in_fence = False
    for i, line in enumerate(raw, 1):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence:
            out.append((i, line))
    return out


def norm(s):
    return re.sub(r'\s+', '', s)


def strip_number(title):
    return re.sub(r'^\d+(?:\.\d+)*\s*', '', title.strip())


def sections(pairs):
    heads = []
    for idx, (lineno, text) in enumerate(pairs):
        m = re.match(r'^(#{1,6})\s+(.+?)\s*$', text)
        if m:
            heads.append({'level': len(m.group(1)), 'title': m.group(2),
                          'line': lineno, 'pos': idx})
    for j, h in enumerate(heads):
        end = heads[j + 1]['pos'] if j + 1 < len(heads) else len(pairs)
        h['body'] = pairs[h['pos'] + 1:end]
    return heads


def find_section(heads, *names):
    wanted = [norm(n) for n in names]
    for h in heads:
        if norm(strip_number(h['title'])) in wanted:
            return h
    for h in heads:
        t = norm(strip_number(h['title']))
        for w in wanted:
            if t.startswith(w):
                return h
    return None


def section_text(heads, sec):
    """sec 的 body 加其所有子节 body（直到同级或更高级标题）。"""
    parts = [t for _, t in sec['body']]
    started = False
    for h in heads:
        if h is sec:
            started = True
            continue
        if not started:
            continue
        if h['level'] <= sec['level']:
            break
        parts.extend(t for _, t in h['body'])
    return '\n'.join(parts)


def subsection_titles(heads, sec):
    out = []
    started = False
    for h in heads:
        if h is sec:
            started = True
            continue
        if not started:
            continue
        if h['level'] <= sec['level']:
            break
        out.append(h['title'])
    return out


def report(tag, errors, warns):
    for e in errors:
        print('[ERROR] ' + e)
    for w in warns:
        print('[WARN]  ' + w)
    if errors:
        print('FAIL %s：%d 个错误，%d 个警告' % (tag, len(errors), len(warns)))
        return 1
    print('结构检查通过 · 语义未验证  %s（%d 个警告）' % (tag, len(warns)))
    print('未覆盖：模板符合度、角色边界、架构可行性')
    return 0


def clean_cell(s):
    return s.strip().strip(chr(96)).strip('*').strip()


def is_placeholder(s):
    s = s.strip()
    return not s or (s.startswith('<') and s.endswith('>'))


def req_ids(path):
    ids = set()
    if not os.path.isfile(path):
        return ids
    for _, line in read_unfenced(path):
        ids.update(ANY_ID.findall(line))
    return ids


def component_defs(heads):
    """返回 [(heading, 名称)]，只认 5.3.4/5.3.5/5.3.6 下的组件定义。"""
    arch = find_section(heads, '软件架构设计')
    if arch is None:
        return []
    out = []
    for h in heads[heads.index(arch) + 1:]:
        if h['level'] <= arch['level']:
            break
        m = re.match(r'^5\.3\.[456]\.\d+\s+(.+)$', h['title'].strip())
        if not m:
            continue
        raw = m.group(1)
        name = clean_cell(re.split(r'定义|/|（', raw)[0])
        name = re.sub(r'^组件', '', name).strip()
        out.append((h, name))
    return out


def main():
    if len(sys.argv) < 2:
        print(__doc__.strip())
        return 2
    base = sys.argv[1]
    path = os.path.join(base, '02-architecture.md')
    spec = os.path.join(base, '01-requirements.md')
    errors, warns = [], []

    if not os.path.isfile(path):
        errors.append('找不到 02-architecture.md')
        return report('check_architecture ' + base, errors, warns)

    raw = open(path, encoding='utf-8').read()
    pairs = read_unfenced(path)
    heads = sections(pairs)
    reqs = req_ids(spec)

    for name in ('简介', '资源', '沟通计划', '软件架构设计', '追溯分析'):
        if find_section(heads, name) is None:
            errors.append('缺少必需章节：' + name)
    for name in ('生产、运行、服务和报废要求', '附录'):
        if find_section(heads, name) is None:
            warns.append('建议补上章节：' + name)

    for layer in LAYERS:
        if not any(h['title'].strip().startswith(layer) and h['level'] == 3
                   for h in heads):
            warns.append('「5.3 软件分解」缺少层级小节：' + layer)

    comps = component_defs(heads)
    seen = set()
    covered = 0
    covered_ids = set()
    if not comps:
        errors.append('「5.3 软件分解」没有组件定义（应形如 #### 5.3.4.1 组件XXX定义）')
    for h, name in comps:
        if not name:
            errors.append('第 %d 行组件定义缺少组件名' % h['line'])
            continue
        if 'XXX' in name or 'xxx' in name:
            warns.append('第 %d 行组件名仍是占位符：%s' % (h['line'], name))
            continue
        if name in seen:
            errors.append('组件名重复：%s' % name)
        seen.add(name)
        body = '\n'.join(t for _, t in h['body'])
        m = re.search(r'覆盖需求\*{0,2}\s*[：:]\s*(.+)', body)
        if not m:
            errors.append('%s 缺少「覆盖需求」：应列出本组件兑现的 SSR/REQ' % name)
            continue
        ids = ANY_ID.findall(m.group(1))
        if not ids:
            errors.append('%s 的「覆盖需求」没有 SSR/REQ 编号' % name)
            continue
        covered += 1
        for rid in ids:
            covered_ids.add(rid)
            if reqs and rid not in reqs:
                errors.append('%s 覆盖了不存在的 %s' % (name, rid))
        subs = [strip_number(t) for t in subsection_titles(heads, h)]
        for key in ('描述', '时序', '接口定义'):
            if not any(s.startswith(key) for s in subs):
                warns.append('%s 建议补子节：%s' % (name, key))

    dyn = find_section(heads, '动态行为')
    if dyn is not None:
        lines = raw.splitlines()
        start = dyn['line'] - 1
        end = len(lines)
        for h in heads:
            if h['line'] > dyn['line'] and h['level'] <= dyn['level']:
                end = h['line'] - 1
                break
        mermaid_count = sum(1 for ln in lines[start:end]
                            if ln.strip().startswith('```mermaid'))
        if mermaid_count == 0:
            warns.append('「5.4 动态行为」建议用一张整体 mermaid 时序图（```mermaid 代码块）')
        elif mermaid_count > 1:
            warns.append('「5.4 动态行为」应只有一张整体时序图，其余阶段用状态解释（当前 %d 张）' % mermaid_count)
        titles = subsection_titles(heads, dyn)
        participants = [m.group(1).strip() for m in
                        re.finditer(r'participant\s+\w+\s+as\s+(.+)',
                                    '\n'.join(lines[start:end]))]
        if participants:
            sub_names = [strip_number(t) for t in titles]
            only_diagram = [p for p in participants if p not in sub_names]
            only_subs = [s for s in sub_names if s not in participants]
            if only_diagram or only_subs:
                warns.append('「5.4 动态行为」图与阶段小节不对齐：图中多出 %s；小节多出 %s'
                             % (only_diagram or '无', only_subs or '无'))

    trace = find_section(heads, '追溯分析')
    if trace is not None and covered_ids:
        ttext = section_text(heads, trace)
        for rid in sorted(covered_ids):
            if rid not in ttext:
                warns.append('追溯分析里没有 %s（建议补一行）' % rid)

    for ln, msg in lint_common.placeholder_issues(raw):
        errors.append('第 %d 行：%s' % (ln, msg))
    if not lint_common.has_role_header(raw, '架构师'):
        errors.append('缺少文档头：> 角色：架构师 ｜ 依据：…')
    warns.extend(lint_common.heading_order_warnings(
        raw, ['简介', '资源', '沟通计划', '软件架构设计',
              '生产、运行、服务和报废要求', '追溯分析', '附录']))

    print('组件：%d ｜ 覆盖需求的组件：%d' % (len(comps), covered))
    return report('check_architecture ' + base, errors, warns)


if __name__ == '__main__':
    sys.exit(main())

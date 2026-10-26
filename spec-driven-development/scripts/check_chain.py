#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""需求链条检查（故事 -> FR -> 任务）。

只查机械事实：每条 FR 是否挂在故事下、是否有任务覆盖、任务引用的 FR/US 是否真实存在；
各文档是否留了修订记录节。

用法: python check_chain.py <项目>/SDD
"""

import re
import sys

FENCE = re.compile(r'^\s*(?:\x60\x60\x60|~~~)')


def read_unfenced(path):
    """读文件，返回 [(行号, 文本)]，跳过围栏代码块（含围栏标记本身）。"""
    with open(path, encoding='utf-8') as fh:
        raw = fh.read().splitlines()
    out = []
    in_fence = False
    for i, ln in enumerate(raw, 1):
        if FENCE.match(ln):
            in_fence = not in_fence
            continue
        if not in_fence:
            out.append((i, ln))
    return out


def norm(s):
    return re.sub(r'\s+', '', s)


def sections(pairs):
    """按 ## / ### 切分，返回 [{level,title,line,body:[[lineno,text]]}]"""
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
    """按归一化标题匹配：先精确匹配，再前缀匹配。"""
    wanted = [norm(n) for n in names]
    for h in heads:
        if norm(h['title']) in wanted:
            return h
    for h in heads:
        t = norm(h['title'])
        for w in wanted:
            if t.startswith(w):
                return h
    return None


def report(tag, errors, warns):
    for e in errors:
        print('[ERROR] ' + e)
    for w in warns:
        print('[WARN]  ' + w)
    if errors:
        print('FAIL %s：%d 个错误，%d 个警告' % (tag, len(errors), len(warns)))
        return 1
    print('结构检查通过 · 语义未验证  %s（%d 个警告）' % (tag, len(warns)))
    print('未覆盖：模板符合度、角色边界、可验收性、可行性')
    return 0

import os

TASK = re.compile(r'^\s*[-*]\s+\[([ xX~])\]\s*T(\d{3})\b')


def load(path):
    if not os.path.isfile(path):
        return None
    pairs = read_unfenced(path)
    return pairs, sections(pairs)


def main():
    if len(sys.argv) < 2:
        print(__doc__.strip())
        return 2
    base = sys.argv[1]
    errors, warns = [], []

    spec = load(os.path.join(base, '01-spec.md'))
    plan = load(os.path.join(base, '02-plan.md'))
    tasks = load(os.path.join(base, '03-tasks.md'))

    for name, doc in [('01-spec.md', spec), ('02-plan.md', plan), ('03-tasks.md', tasks)]:
        if doc is None:
            errors.append('找不到 ' + name)
    if errors:
        return report('check_chain ' + base, errors, warns)

    spec_pairs, spec_heads = spec
    task_pairs, task_heads = tasks

    for name, heads in [('01-spec.md', spec_heads), ('02-plan.md', plan[1]), ('03-tasks.md', task_heads)]:
        if find_section(heads, '修订记录') is None:
            errors.append('%s 缺少「修订记录」节' % name)

    stories = {}
    for h in spec_heads:
        m = re.match(r'^US\s*(\d+)', norm(h['title']))
        if m:
            stories[int(m.group(1))] = h

    fr_def = {}
    sec = find_section(spec_heads, '功能需求')
    for _, t in (sec['body'] if sec else []):
        m = re.match(r'^\s*[-*]?\s*\*\*(FR-\d{3})\*\*', t)
        if m:
            fr_def[int(m.group(1).split('-')[1])] = None

    for n, h in stories.items():
        body = '\n'.join(t for _, t in h['body'])
        for m in re.finditer(r'FR-(\d{3})', body):
            fr_def[int(m.group(1))] = n

    task_text = '\n'.join(t for _, t in task_pairs if TASK.match(t))
    task_fr = set(int(m.group(1)) for m in re.finditer(r'FR-(\d{3})', task_text))
    task_us = set(int(m.group(1)) for m in re.finditer(r'US\s*(\d+)', task_text))

    for n in sorted(fr_def):
        if fr_def[n] is None:
            warns.append('FR-%03d 没有挂在任何用户故事下' % n)
        if n not in task_fr:
            errors.append('FR-%03d 没有任务覆盖（链条断了）' % n)
    for n in sorted(task_fr - set(fr_def)):
        errors.append('03-tasks.md 引用了不存在的 FR-%03d（幽灵引用）' % n)
    for n in sorted(task_us - set(stories)):
        errors.append('03-tasks.md 引用了不存在的 US%d' % n)

    plan_text = '\n'.join(t for _, t in plan[0])
    if not re.search(r'宪法检查', plan_text):
        warns.append('02-plan.md 里没有找到「宪法检查」节')
    if not re.search(r'验证手段', plan_text):
        warns.append('02-plan.md 里没有找到「验证手段」节')

    print('链条：故事 %d ｜ FR %d ｜ 被任务覆盖的 FR %d'
          % (len(stories), len(fr_def), len(task_fr & set(fr_def))))
    return report('check_chain ' + base, errors, warns)


if __name__ == '__main__':
    sys.exit(main())

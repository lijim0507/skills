#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""追溯链检查：REQ（01）→ 模块 / 公开接口（02）→ 函数（03，一模块一份）→ 任务（04）。

只查机械事实：每条 REQ 都有架构落点与任务落点、引用的编号存在、模块清单与详细设计文件一致。
不检查覆盖是否“真”成立；那是人确认与验证阶段的事。

用法: python check_chain.py <项目>/SDD
"""

import glob
import os
import re
import sys

FENCE = re.compile(r'^\s*(?:\x60\x60\x60|~~~)')
REQ_ID = r'REQ(?:-[A-Za-z0-9]+)+'
REQ_DEF = re.compile(r'^\s*\*\*\s*\[?(' + REQ_ID + r')\]?\s*(.*?)\s*\*\*\s*$')
REQ_IN_TEXT = re.compile(r'\b(' + REQ_ID + r')\b')
TASK_LINE = re.compile(r'^\s*[-*]\s+\[[ xX~]\]\s+(T\d{3})\b(.+)$')
TASK_TAG = re.compile(r'(?:REQ(?:-[A-Za-z0-9]+)+|R-\d{2,3})')
NON_MODULE = {'数据质量', '交接给实现', '修订记录'}


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


def report(tag, errors, warns):
    for e in errors:
        print('[ERROR] ' + e)
    for w in warns:
        print('[WARN]  ' + w)
    if errors:
        print('FAIL %s：%d 个错误，%d 个警告' % (tag, len(errors), len(warns)))
        return 1
    print('结构检查通过 · 语义未验证  %s（%d 个警告）' % (tag, len(warns)))
    print('未覆盖：覆盖是否真成立、验证证据是否充分')
    return 0


def is_separator(cells):
    return all(re.fullmatch(r':?-{2,}:?', c.replace(' ', '')) for c in cells if c)


def table_rows(body):
    rows = []
    for lineno, text in body:
        s = text.strip()
        if not s.startswith('|'):
            continue
        cells = [c.strip() for c in s.strip('|').split('|')]
        if not cells or is_separator(cells):
            continue
        rows.append((lineno, cells))
    return rows


def col_index(header, *keywords):
    for i, h in enumerate(header):
        hn = norm(h)
        if all(k in hn for k in keywords):
            return i
    return None


def clean_cell(s):
    return s.strip().strip(chr(96)).strip('*').strip()


def parse_reqs(path):
    if not os.path.isfile(path):
        return {}
    heads = sections(read_unfenced(path))
    sec = find_section(heads, '软件需求')
    if sec is None:
        return {}
    body = list(sec['body'])
    started = False
    for h in heads:
        if h is sec:
            started = True
            continue
        if not started:
            continue
        if h['level'] <= sec['level']:
            break
        body.extend(h['body'])
    defs = {}
    for lineno, t in body:
        m = REQ_DEF.match(t)
        if m:
            defs[clean_cell(m.group(1))] = lineno
    return defs


def arch_info(path):
    """返回 (模块集合, 模块→覆盖 REQ 列表)。"""
    modules, cover = set(), {}
    if not os.path.isfile(path):
        return modules, cover
    heads = sections(read_unfenced(path))
    sec = find_section(heads, '模块清单')
    if sec is not None:
        rows = table_rows(sec['body'])
        if rows:
            idx = col_index(rows[0][1], '模块')
            if idx is not None:
                for _, cells in rows[1:]:
                    if len(cells) > idx:
                        name = clean_cell(cells[idx])
                        if name and not (name.startswith('<') and name.endswith('>')):
                            modules.add(name)
    csec = find_section(heads, '模块契约')
    if csec is not None:
        start = heads.index(csec)
        for h in heads[start + 1:]:
            if h['level'] <= 2:
                break
            if h['level'] == 3:
                # 层标题：应用层 / 中间层 / 驱动层
                continue
            if h['level'] != 4:
                continue
            name = clean_cell(strip_number(h['title']))
            if not name or (name.startswith('<') and name.endswith('>')):
                continue
            text = '\n'.join(t for _, t in h['body'])
            m = re.search(r'\*\*覆盖 REQ\*\*\s*[：:]\s*(.+)', text)
            cover[name] = REQ_IN_TEXT.findall(m.group(1)) if m else []
    return modules, cover


def design_files(base):
    """一个模块一份：03-design-<模块>.md，模块名从文件名取。"""
    files = sorted(glob.glob(os.path.join(base, '03-design-*.md')))
    out = []
    for path in files:
        name = os.path.basename(path)
        if name.startswith('03-design-') and name.endswith('.md'):
            out.append((name[len('03-design-'):-len('.md')], path))
    return out


def task_reqs(path):
    if not os.path.isfile(path):
        return []
    refs = []
    for _, text in read_unfenced(path):
        m = TASK_LINE.match(text)
        if m:
            refs.extend(TASK_TAG.findall(text))
    return refs


def main():
    if len(sys.argv) < 2:
        print(__doc__.strip())
        return 2
    base = sys.argv[1]
    errors, warns = [], []

    spec = os.path.join(base, '01-requirements.md')
    arch = os.path.join(base, '02-architecture.md')
    impl = os.path.join(base, '04-implementation.md')

    reqs = parse_reqs(spec)
    modules, cover = arch_info(arch)
    dmods = design_files(base)
    dnames = {m for m, _ in dmods}
    trefs = task_reqs(impl)

    if not reqs:
        errors.append('没读到 01-requirements.md 的 REQ 定义')
    if not modules:
        errors.append('没读到 02-architecture.md 的模块清单')
    if not dmods:
        errors.append('没读到 03-design-<模块>.md（一个模块一份）')
    if not trefs:
        errors.append('没读到 04-implementation.md 的任务行')

    covered_by_arch = set()
    for name, rids in cover.items():
        for rid in rids:
            covered_by_arch.add(rid)
            if rid not in reqs:
                errors.append('%s 的「覆盖 REQ」引用了不存在的 %s' % (name, rid))

    covered_by_task = set()
    for rid in trefs:
        covered_by_task.add(rid)
        if rid not in reqs:
            errors.append('任务行引用了不存在的 %s' % rid)

    for rid in sorted(set(reqs) - covered_by_arch):
        errors.append('%s 没有被任何架构模块覆盖（链条断了）' % rid)
    for rid in sorted(set(reqs) - covered_by_task):
        errors.append('%s 没有被任何任务覆盖（链条断了）' % rid)

    for name in sorted(dnames - modules):
        errors.append('详细设计有架构清单中没有的模块：%s' % name)
    for name in sorted(modules - dnames):
        errors.append('架构模块没有详细设计文件：03-design-%s.md' % name)
    for name in sorted(set(cover) - modules):
        errors.append('模块契约里有模块清单中没有的模块：%s' % name)

    for label, path in (('01', spec), ('02', arch), ('04', impl)):
        if not os.path.isfile(path):
            warns.append('找不到 %s 文档：%s' % (label, path))
            continue
        heads = sections(read_unfenced(path))
        if label == '01':
            ok = (find_section(heads, '修订记录') is not None
                  or find_section(heads, '变更历史') is not None)
            if not ok:
                errors.append('01 文档缺少「修订记录」或「变更历史」')
        elif find_section(heads, '修订记录') is None:
            errors.append('%s 文档缺少「修订记录」' % label)

    for _, path in dmods:
        heads = sections(read_unfenced(path))
        if find_section(heads, '修订记录') is None:
            errors.append('%s 缺少「修订记录」' % os.path.basename(path))

    print('链条：REQ %d ｜ 被架构覆盖 %d ｜ 被任务覆盖 %d'
          % (len(reqs), len(set(reqs) & covered_by_arch), len(set(reqs) & covered_by_task)))
    return report('check_chain ' + base, errors, warns)


if __name__ == '__main__':
    sys.exit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""详细设计检查（03-design-<模块>.md，SWE.3 结构，一个模块一份）。

只查机械事实：每个架构模块是否有对应文件、章节是否齐全、
「8.2 软件单元」下是否有单元分组、每组有「函数设计」表（含函数编号 / 所在文件）、
可追溯性引用 REQ、文档头与章节顺序。
函数是否够细、状态与流程是否完整由人确认前判断。

用法: python check_design.py <项目>/SDD
"""

import glob
import os
import re
import sys
import lint_common

FENCE = re.compile(r'^\s*(?:\x60\x60\x60|~~~)')
REQ_ID = r'REQ(?:-[A-Za-z0-9]+)+'
REQ_IN_TEXT = re.compile(r'\b(' + REQ_ID + r')\b')
NON_UNIT = {'单元说明', '函数设计'}
DESIGN_GLOB = '03-design-*.md'
DESIGN_PREFIX = '03-design-'
DESIGN_SUFFIX = '.md'


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


def module_body(pairs, heads, h):
    """从 h 到下一个同级或更高级标题之间的所有行（含更深的子标题）。"""
    end = len(pairs)
    for nxt in heads:
        if nxt['pos'] > h['pos'] and nxt['level'] <= h['level']:
            end = nxt['pos']
            break
    return pairs[h['pos'] + 1:end]


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


def report(tag, errors, warns):
    for e in errors:
        print('[ERROR] ' + e)
    for w in warns:
        print('[WARN]  ' + w)
    if errors:
        print('FAIL %s：%d 个错误，%d 个警告' % (tag, len(errors), len(warns)))
        return 1
    print('结构检查通过 · 语义未验证  %s（%d 个警告）' % (tag, len(warns)))
    print('未覆盖：模板符合度、角色边界、设计完整性')
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


def arch_modules(path):
    """从 02 的模块清单读模块名。"""
    if not os.path.isfile(path):
        return []
    heads = sections(read_unfenced(path))
    sec = find_section(heads, '模块清单')
    if sec is None:
        return []
    rows = table_rows(sec['body'])
    if not rows:
        return []
    idx = col_index(rows[0][1], '模块')
    if idx is None:
        return []
    mods = []
    for _, cells in rows[1:]:
        if len(cells) <= idx:
            continue
        name = clean_cell(cells[idx])
        if name and not (name.startswith('<') and name.endswith('>')):
            mods.append(name)
    return mods


def design_files(base):
    return sorted(glob.glob(os.path.join(base, DESIGN_GLOB)))


def module_from_file(path):
    name = os.path.basename(path)
    if name.startswith(DESIGN_PREFIX) and name.endswith(DESIGN_SUFFIX):
        return name[len(DESIGN_PREFIX):-len(DESIGN_SUFFIX)]
    return None


def check_one(path, errors, warns):
    """检查一个 03 文件，返回软件单元数量。"""
    pairs = read_unfenced(path)
    heads = sections(pairs)
    units = 0

    for name in ('简介', '资源', '沟通计划', '软件组件描述',
                 '接口', '软件组件设计', '软件单元设计', '可追溯性', '附录'):
        if find_section(heads, name) is None:
            errors.append('%s 缺少必需章节：%s' % (os.path.basename(path), name))

    # 8.2 软件单元：每个单元一个 #### 分组
    unit_sec = find_section(heads, '软件单元', '函数设计')
    groups = {}
    if unit_sec is not None:
        start = heads.index(unit_sec)
        for h in heads[start + 1:]:
            if h['level'] <= unit_sec['level']:
                break
            if h['level'] != unit_sec['level'] + 1:
                continue
            name = clean_cell(strip_number(h['title']))
            if not name or norm(name) in NON_UNIT:
                continue
            if name in groups:
                errors.append('%s 的软件单元分组重复：%s' % (os.path.basename(path), name))
            groups[name] = h
            body = module_body(pairs, heads, h)
            text = '\n'.join(t for _, t in body)
            if '函数设计' not in text:
                errors.append('%s 的 %s 缺少「函数设计」表' % (os.path.basename(path), name))
            else:
                rows = table_rows(body)
                header = rows[0][1] if rows else None
                if header is not None and any('函数' in c for c in header):
                    if col_index(header, '函数', '编号') is None:
                        warns.append('%s 的 %s 函数设计表建议加「函数编号」列'
                                     % (os.path.basename(path), name))
                    if col_index(header, '文件') is None:
                        warns.append('%s 的 %s 函数设计表建议加「所在文件」列'
                                     % (os.path.basename(path), name))
            for key in ('参数', '私有数据', '状态与流程', '动态特性', '错误处理', '不变量与约束'):
                if key not in text:
                    warns.append('%s 的 %s 建议补上「%s」'
                                 % (os.path.basename(path), name, key))
            if not re.search(r'\|', text):
                warns.append('%s 的 %s 没有表格（函数设计至少应是一张表）'
                             % (os.path.basename(path), name))

    units += len(groups)

    # 可追溯性：需求 → 详设 表应引用 REQ
    trace = find_section(heads, '可追溯性')
    if trace is not None:
        ttext = section_text(heads, trace)
        if not REQ_IN_TEXT.findall(ttext):
            warns.append('%s 的「可追溯性」建议列出 需求 → 详设 的映射'
                         % os.path.basename(path))
    else:
        errors.append('%s 缺少「可追溯性」节' % os.path.basename(path))

    # 附录：数据质量 / 交接给实现
    appendix = find_section(heads, '附录')
    if appendix is not None:
        atext = '\n'.join(t for _, t in appendix['body'])
        if '数据质量' not in atext:
            warns.append('%s 的「附录」建议含「数据质量」' % os.path.basename(path))
        if '交接给实现' not in atext:
            warns.append('%s 的「附录」建议含「交接给实现」' % os.path.basename(path))

    raw = open(path, encoding='utf-8').read()
    for ln, msg in lint_common.placeholder_issues(raw):
        errors.append('%s 第 %d 行：%s' % (os.path.basename(path), ln, msg))
    if not lint_common.has_role_header(raw, '详细设计师'):
        errors.append('%s 缺少文档头：> 角色：详细设计师 ｜ 依据：…' % os.path.basename(path))
    warns.extend(lint_common.heading_order_warnings(
        raw, ['简介', '资源', '沟通计划', '软件组件描述', '接口',
              '软件组件设计', '软件单元设计', '可追溯性', '附录']))
    return units


def main():
    if len(sys.argv) < 2:
        print(__doc__.strip())
        return 2
    base = sys.argv[1]
    arch = os.path.join(base, '02-architecture.md')
    errors, warns = [], []

    files = design_files(base)
    if not files:
        errors.append('找不到 03-design-<模块>.md（一个模块一份）')
        return report('check_design ' + base, errors, warns)

    modules = arch_modules(arch)
    if not modules:
        warns.append('没有从 02-architecture.md 读到模块清单，无法核对覆盖')

    seen = {}
    total_units = 0
    for path in files:
        mod = module_from_file(path)
        if mod is None:
            warns.append('文件命名不符合 03-design-<模块>.md：%s' % os.path.basename(path))
            continue
        if mod in seen:
            errors.append('同一模块有多份详细设计：%s / %s'
                          % (os.path.basename(seen[mod]), os.path.basename(path)))
        seen[mod] = path
        total_units += check_one(path, errors, warns)

    for name in modules:
        if name not in seen:
            errors.append('架构模块没有详细设计文件：03-design-%s.md' % name)
    for name in sorted(set(seen) - set(modules)):
        errors.append('详细设计有架构清单中没有的模块：%s' % name)

    print('详细设计：模块 %d / %d ｜ 文件 %d ｜ 软件单元 %d'
          % (len(set(modules) & set(seen)), len(modules), len(seen), total_units))
    return report('check_design ' + base, errors, warns)


if __name__ == '__main__':
    sys.exit(main())

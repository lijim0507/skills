#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""详细设计检查（03-design-<组件>.md，SWE.3 结构，一个组件一份）。

只查机械事实：每个架构组件是否有对应文件、章节是否齐全、
「8 软件单元设计」下每个软件单元是否有「函数设计」表、可追溯性引用 SSR/REQ、
文档头与章节顺序。
函数是否够细、状态与流程是否完整由人确认前判断。

用法: python check_design.py <项目>/SDD
"""

import glob
import os
import re
import sys
import lint_common

FENCE = re.compile(r'^\s*(?:\x60\x60\x60|~~~)')
SSR_ID = r'SSR\d{3,}'
REQ_ID = r'REQ(?:-[A-Za-z0-9]+)+'
ANY_ID = re.compile(r'\b(' + SSR_ID + r'|' + REQ_ID + r')\b')
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
        parts.append(h['title'])
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


def component_defs(heads):
    """从 02 的 5.3.4/5.3.5/5.3.6 组件定义读组件名。"""
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
        name = clean_cell(re.split(r'定义|/|（', m.group(1))[0])
        name = re.sub(r'^组件', '', name).strip()
        if name:
            out.append(name)
    return out


def arch_modules(path):
    if not os.path.isfile(path):
        return []
    heads = sections(read_unfenced(path))
    return [n for n in component_defs(heads) if 'XXX' not in n and 'xxx' not in n]


def design_files(base):
    files = sorted(glob.glob(os.path.join(base, DESIGN_GLOB)))
    if not files:
        # 模板目录只有一份 03-design.md：把它当作空模块名来检查内容
        plain = os.path.join(base, '03-design.md')
        if os.path.isfile(plain):
            files = [plain]
    return files


def module_from_file(path):
    name = os.path.basename(path)
    if name == '03-design.md':
        return ''
    if name.startswith(DESIGN_PREFIX) and name.endswith(DESIGN_SUFFIX):
        return name[len(DESIGN_PREFIX):-len(DESIGN_SUFFIX)]
    return None


def check_one(path, errors, warns):
    """检查一个 03 文件，返回软件单元数量。"""
    pairs = read_unfenced(path)
    heads = sections(pairs)
    units = 0
    fname = os.path.basename(path)

    for name in ('简介', '资源', '沟通计划', '软件组件描述',
                 '接口', '软件组件设计', '软件单元设计', '可追溯性', '附录'):
        if find_section(heads, name) is None:
            errors.append('%s 缺少必需章节：%s' % (fname, name))

    # 8 软件单元设计：8.1 代码生成配置之后的 8.x 才是软件单元
    unit_sec = find_section(heads, '软件单元设计', '软件单元')
    if unit_sec is not None:
        start = heads.index(unit_sec)
        for h in heads[start + 1:]:
            if h['level'] <= unit_sec['level']:
                break
            if h['level'] != unit_sec['level'] + 1:
                continue
            name = clean_cell(strip_number(h['title']))
            if not name or '代码生成配置' in name:
                continue
            body = module_body(pairs, heads, h)
            text = '\n'.join(t for _, t in body)
            if '函数设计' not in text:
                errors.append('%s 的 %s 缺少「函数设计」表' % (fname, name))
            else:
                units += 1
                rows = table_rows(body)
                fheader = None
                for _, cells in rows:
                    if any('函数' in c for c in cells):
                        fheader = cells
                        break
                if fheader is not None:
                    if (col_index(fheader, '函数', '编号') is None
                            and col_index(fheader, '函数', 'ID') is None):
                        warns.append('%s 的 %s 函数设计表建议加「函数编号/函数ID」列'
                                     % (fname, name))
                    if (col_index(fheader, '文件') is None
                            and find_section(heads, '源代码文件清单', '文件清单') is None):
                        warns.append('%s 的 %s 函数设计表建议加「所在文件」列，或在 7.2.4 源代码文件清单中给出'
                                     % (fname, name))
                for key in ('参数', '私有数据', '状态与流程', '动态特性', '错误处理', '不变量与约束'):
                    if key not in text:
                        warns.append('%s 的 %s 建议补上「%s」' % (fname, name, key))

    # 可追溯性：需求 → 详设 表应引用 SSR/REQ
    trace = find_section(heads, '可追溯性')
    if trace is not None:
        ttext = section_text(heads, trace)
        if not ANY_ID.findall(ttext):
            warns.append('%s 的「可追溯性」建议列出 需求 → 详设 的映射' % fname)
    else:
        errors.append('%s 缺少「可追溯性」节' % fname)

    appendix = find_section(heads, '附录')
    if appendix is not None:
        atext = section_text(heads, appendix)
        if '数据质量' not in atext:
            warns.append('%s 的「附录」建议含「数据质量」' % fname)
        if '交接给实现' not in atext:
            warns.append('%s 的「附录」建议含「交接给实现」' % fname)

    raw = open(path, encoding='utf-8').read()
    for ln, msg in lint_common.placeholder_issues(raw):
        errors.append('%s 第 %d 行：%s' % (fname, ln, msg))
    if not lint_common.has_role_header(raw, '详细设计师'):
        errors.append('%s 缺少文档头：> 角色：详细设计师 ｜ 依据：…' % fname)
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
        errors.append('找不到 03-design-<组件>.md（一个组件一份）')
        return report('check_design ' + base, errors, warns)

    modules = arch_modules(arch)
    if not modules:
        warns.append('没有从 02-architecture.md 读到 5.3 组件定义，无法核对覆盖')

    seen = {}
    total_units = 0
    for path in files:
        mod = module_from_file(path)
        if mod is None:
            warns.append('文件命名不符合 03-design-<组件>.md：%s' % os.path.basename(path))
            continue
        if mod == '':
            warns.append('%s 是模板文件名（未写组件名），跳过组件归属核对' % os.path.basename(path))
            total_units += check_one(path, errors, warns)
            continue
        if mod in seen:
            errors.append('同一组件有多份详细设计：%s / %s'
                          % (os.path.basename(seen[mod]), os.path.basename(path)))
        seen[mod] = path
        total_units += check_one(path, errors, warns)

    for name in modules:
        if name not in seen:
            errors.append('架构组件没有详细设计文件：03-design-%s.md' % name)
    for name in sorted(set(seen) - set(modules)):
        errors.append('详细设计有架构清单中没有的组件：%s' % name)

    print('详细设计：组件 %d / %d ｜ 文件 %d ｜ 软件单元 %d'
          % (len(set(modules) & set(seen)), len(modules), len(seen), total_units))
    return report('check_design ' + base, errors, warns)


if __name__ == '__main__':
    sys.exit(main())

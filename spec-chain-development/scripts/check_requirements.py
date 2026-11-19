#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""软件需求检查（01-requirements.md，SWE.1 结构）。

只查机械事实：章节是否齐全、REQ 编号唯一、每条 REQ 有需求编号 / 描述 / 验证准则 / 依赖、
需求清单与正文一致、追溯分析覆盖所有 REQ、正文引用存在。
不检查需求是否可验收；那是人确认前的事。

用法: python check_requirements.py <项目>/SDD/01-requirements.md
"""

import os
import re
import sys
import lint_common

FENCE = re.compile(r'^\s*(?:\x60\x60\x60|~~~)')
REQ_ID = r'REQ(?:-[A-Za-z0-9]+)+'
SSR_ID = r'SSR\d{3,}'
REQ_DEF = re.compile(r'^\s*\*\*\s*\[?(' + REQ_ID + r')\]?\s*(.*?)\s*\*\*\s*$')
REQ_IN_TEXT = re.compile(r'\b(' + REQ_ID + r')\b')
SSR_IN_TEXT = re.compile(r'\b(' + SSR_ID + r')\b')
ANY_ID_IN_TEXT = re.compile(r'\b((?:' + REQ_ID + r')|(?:' + SSR_ID + r'))\b')


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


def table_rows(body):
    """返回第一张连续表格的 (行号, 单元格列表)；跳过对齐分隔行。"""
    rows = []
    for lineno, t in body:
        s = t.strip()
        if not (s.startswith('|') and s.endswith('|')):
            if rows:
                break
            continue
        cells = [c.strip() for c in s.strip('|').split('|')]
        rows.append((lineno, cells))
    if len(rows) >= 2 and all(re.match(r'^:?-{2,}:?$', c) for c in rows[1][1]):
        rows = [rows[0]] + rows[2:]
    return rows


def all_tables(body):
    """返回 body 里所有表格的表头与数据行。"""
    tables = []
    cur = None
    for lineno, t in body:
        s = t.strip()
        if s.startswith('|') and s.endswith('|'):
            cells = [c.strip() for c in s.strip('|').split('|')]
            if all(re.match(r'^:?-{2,}:?$', c) for c in cells if c):
                continue
            if cur is None:
                cur = {'header': cells, 'rows': [], 'line': lineno}
                tables.append(cur)
            else:
                cur['rows'].append((lineno, cells))
        elif cur is not None:
            cur = None
    return tables


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
    print('未覆盖：模板符合度、角色边界、可验收性')
    return 0


def parse_reqs(heads):
    """返回 (软件需求节, 块列表)；块 = {id, line, body}。"""
    sec = find_section(heads, '软件需求')
    if sec is None:
        return None, []
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
    blocks = []
    cur = None
    for lineno, t in body:
        m = REQ_DEF.match(t)
        if m:
            cur = {'id': m.group(1), 'line': lineno, 'body': []}
            blocks.append(cur)
        elif cur is not None:
            if re.match(r'^#{1,6}\s+', t):
                cur = None
            else:
                cur['body'].append((lineno, t))
    return sec, blocks


def section_lines(heads, sec):
    """sec 的 body 加其所有子节 body（保留行号，供表格解析）。"""
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
    return body


def parse_ssr_cards(heads):
    """解析 SWE.1 需求卡：| 需求 ID | SSR001 | 后接键值行。"""
    sec = find_section(heads, '软件需求')
    if sec is None:
        return None, []
    cards = []
    cur = None
    for lineno, t in section_lines(heads, sec):
        if re.match(r'^#{1,6}\s+', t):
            cur = None
            continue
        s = t.strip()
        if not (s.startswith('|') and s.endswith('|')):
            continue
        cells = [c.strip() for c in s.strip('|').split('|')]
        if not cells:
            continue
        key = norm(cells[0])
        if key in ('需求ID', '需求编号') and len(cells) > 1 and re.fullmatch(SSR_ID, cells[1]):
            cur = {'id': cells[1], 'line': lineno, 'fields': {}}
            cards.append(cur)
            continue
        if cur is None:
            continue
        if all(re.match(r'^:?-{2,}:?$', c) for c in cells if c):
            continue
        val = ' '.join(c for c in cells[1:] if c).strip()
        cur['fields'].setdefault(key, []).append(val)
    return sec, cards


def main():
    if len(sys.argv) < 2:
        print(__doc__.strip())
        return 2
    path = sys.argv[1]
    pairs = read_unfenced(path)
    heads = sections(pairs)
    errors, warns = [], []

    for name in ('概述', '软件需求', '追溯分析'):
        if find_section(heads, name) is None:
            errors.append('缺少必需章节：' + name)
    intro = find_section(heads, '简介', '软件需求简介')
    if intro is None:
        warns.append('建议补上小节：2.1 软件需求简介（需求清单 / 需求间依赖关系）')
    else:
        itext = section_text(heads, intro)
        started = False
        for h in heads:
            if h is intro:
                started = True
                continue
            if not started:
                continue
            if h['level'] <= intro['level']:
                break
            itext += '\n' + h['title']
        if '需求清单' not in itext:
            warns.append('「简介」建议含「需求清单」表')
        if '依赖关系' not in itext:
            warns.append('「简介」建议含「软件需求之间的依赖关系」表')

    sec, blocks = parse_reqs(heads)
    ssr_sec, cards = parse_ssr_cards(heads)
    defs = {}
    for b in blocks:
        if b['id'] in defs:
            errors.append('REQ 编号重复：%s' % b['id'])
            continue
        defs[b['id']] = b
        text = '\n'.join(t for _, t in b['body'])
        if not re.search(r'\*\*需求编号\*\*', text):
            errors.append('%s 缺少「**需求编号**」行（编号 ｜ 类别 ｜ 来源）' % b['id'])
        if not re.search(r'\*\*需求类别\*\*', text):
            warns.append('%s 缺少「**需求类别**」（功能性 / 非功能性 / 接口）' % b['id'])
        if not re.search(r'\*\*描述\*\*', text):
            errors.append('%s 缺少「**描述**」' % b['id'])
        if not re.search(r'\*\*验证准则\*\*', text):
            errors.append('%s 缺少「**验证准则**」' % b['id'])
        items = [t for _, t in b['body'] if re.match(r'^\s*-\s+', t)]
        if not items:
            errors.append('%s 的验证准则没有子条目（至少一条「- …」）' % b['id'])
        if not re.search(r'\*\*依赖\*\*', text):
            warns.append('%s 缺少「**依赖**」（没有依赖写「无」）' % b['id'])

    for c in cards:
        if c['id'] in defs:
            errors.append('需求编号重复：%s' % c['id'])
            continue
        defs[c['id']] = c
        f = {k: ' '.join(v).strip() for k, v in c['fields'].items()}
        if not f.get('需求描述'):
            errors.append('%s 缺少「需求描述」或内容为空' % c['id'])
        if not f.get('验证准则'):
            errors.append('%s 缺少「验证准则」或内容为空' % c['id'])
        if not f.get('验证方法'):
            warns.append('%s 缺少「验证方法」（评审 / 测试 / 仿真 / 分析）' % c['id'])
        if not f.get('需求类别'):
            warns.append('%s 缺少「需求类别」（功能性 / 非功能性 / 接口 / 标题 / 信息）' % c['id'])
        if not (f.get('来源人') or f.get('来源于') or f.get('来源')):
            warns.append('%s 缺少「来源人/来源于」或「来源」（TSR ID + ASIL）' % c['id'])
        if not f.get('需求状态'):
            warns.append('%s 缺少「需求状态」' % c['id'])
        if not f.get('需求分析'):
            warns.append('%s 缺少「需求分析」（技术可行性 / 可验证性 / 成本进度 / 运行环境）' % c['id'])
    if sec is not None and not blocks and not cards:
        errors.append('「软件需求」里没有需求条目（支持 **REQ-…** 块或 | 需求 ID | SSR001 | 需求卡）')

    # 需求清单表：在「简介」节及其子节里找含 REQ 的表头
    if intro is not None:
        body = list(intro['body'])
        started = False
        for h in heads:
            if h is intro:
                started = True
                continue
            if not started:
                continue
            if h['level'] <= intro['level']:
                break
            body.extend(h['body'])
        tables = all_tables(body)
        list_table = None
        for tb in tables:
            if any(('REQ' in c.upper() or '需求ID' in c or '需求 ID' in c) for c in tb['header']):
                list_table = tb
                break
        if list_table is None:
            if cards:
                warns.append('「简介」缺少需求清单表（软件需求ID / 描述 / 备注）')
        else:
            idx = None
            for i, c in enumerate(list_table['header']):
                if 'REQ' in c.upper() or '需求ID' in c or '需求 ID' in c:
                    idx = i
                    break
            for lineno, cells in list_table['rows']:
                if idx is not None and idx < len(cells):
                    for rid in ANY_ID_IN_TEXT.findall(cells[idx]):
                        if rid not in defs:
                            errors.append('第 %d 行：需求清单里的 %s 没有正文定义' % (lineno, rid))

    # 追溯分析：3.1 表覆盖所有 REQ
    trace = find_section(heads, '追溯分析')
    if trace is not None:
        ttext = section_text(heads, trace)
        for rid in defs:
            if rid not in ttext:
                warns.append('追溯分析里没有 %s（建议在「系统需求 → 软件需求」表补一行）' % rid)

    raw = open(path, encoding='utf-8').read()
    for rid in sorted(set(ANY_ID_IN_TEXT.findall(raw))):
        if rid not in defs:
            errors.append('正文引用了不存在的 %s' % rid)
    for ln, msg in lint_common.placeholder_issues(raw):
        errors.append('第 %d 行：%s' % (ln, msg))
    if not lint_common.has_role_header(raw, '需求分析师'):
        errors.append('缺少文档头：> 角色：需求分析师 ｜ 依据：…')
    warns.extend(lint_common.heading_order_warnings(
        raw, ['概述', '软件需求', '追溯分析']))

    print('SSR/REQ：%d' % (len(blocks) + len(cards)))
    return report('check_requirements ' + path, errors, warns)


if __name__ == '__main__':
    sys.exit(main())

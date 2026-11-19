#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""执行编写检查（04-implementation.md）。

只查机械事实：任务表 / 任务行格式与挂接、任务卡是否齐全、必填字段是否为空、覆盖映射表、
文档头与章节顺序。任务拆得好不好、DoD 是否够硬由人确认前判断。

用法: python check_implementation.py <项目>/SDD/04-implementation.md
"""

import re
import sys
import lint_common

FENCE = re.compile(r'^\s*(?:\x60\x60\x60|~~~)')
TASK_LINE = re.compile(r'^\s*[-*]\s+\[[ xX~]\]\s+(T\d{3})\b(.+)$')
TASK_TAG = re.compile(r'(?:REQ(?:-[A-Za-z0-9]+)+|SSR\d+|R-\d{2,3})')
FLOW_TAG = re.compile(r'\|\s*流程\s*$')
CARD_HEAD = re.compile(r'^#{2,6}\s+(T\d{3})\b')
CARD_FIELDS = ['归属', '批次', '执行者', '验收人', '目标', '范围', '输入', '产出',
               '完成判据', '验收判据', '验证', '证据', '依赖']
CARD_REQUIRED = {'归属', '目标', '范围', '输入', '产出', '完成判据',
                 '验收判据', '验证', '证据', '依赖'}


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
    print('未覆盖：模板符合度、角色边界、任务可执行性')
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


def card_fields(body):
    """收集卡内字段：粗体列表（旧写法）与两列表格（模板）都支持。"""
    fields = {}
    for _, text in body:
        m = re.match(r'^\s*[-*]?\s*\*\*([^*]+)\*\*\s*[：:]\s*(.*)$', text)
        if m:
            fields[norm(m.group(1))] = m.group(2).strip()
    known = {norm(n) for n in CARD_FIELDS}
    known |= {norm(n) for n in ('类型', '覆盖需求', '可并行', '规模', '风险 / 回滚')}
    for _, cells in table_rows(body):
        if len(cells) < 2:
            continue
        name = norm(clean_cell(cells[0]))
        if (name in known or any(name.startswith(k) for k in known)) and name not in fields:
            fields[name] = cells[1].strip()
    return fields


def field_value(fields, name):
    """按前缀取字段值，兼容「完成判据（DoD）」这类带注解的字段名。"""
    if name in fields:
        return fields[name]
    for k, v in fields.items():
        if k.startswith(name):
            return v
    return None


def table_tasks(heads):
    """从「任务」章节的表格提取任务；返回 {任务号: (行号, 覆盖需求单元格)}。"""
    sec = find_section(heads, '任务')
    if sec is None:
        return {}
    rows = table_rows(sec['body'])
    if not rows:
        return {}
    header = rows[0][1]
    data = rows
    first = clean_cell(header[0]) if header else ''
    if not re.fullmatch(r'T\d{3}', first):
        data = rows[1:]
    idx_req = col_index(header, '覆盖需求')
    if idx_req is None:
        idx_req = col_index(header, '需求')
    out = {}
    for lineno, cells in data:
        tid = clean_cell(cells[0]) if cells else ''
        if not re.fullmatch(r'T\d{3}', tid):
            continue
        if idx_req is not None and idx_req < len(cells):
            tag_text = cells[idx_req]
        else:
            tag_text = ' '.join(cells[1:])
        out[tid] = (lineno, tag_text)
    return out


def main():
    if len(sys.argv) < 2:
        print(__doc__.strip())
        return 2
    path = sys.argv[1]
    pairs = read_unfenced(path)
    heads = sections(pairs)
    errors, warns = [], []

    for name in ('任务', '覆盖映射'):
        if find_section(heads, name) is None:
            errors.append('缺少必需章节：' + name)
    for name in ('执行说明', '执行批次', '任务卡'):
        if find_section(heads, name) is None:
            warns.append('建议补上章节：' + name)

    # 任务：列表写法（旧文档 / 示例）与表格写法（模板）
    tasks = {}
    for lineno, text in pairs:
        m = TASK_LINE.match(text)
        if not m:
            continue
        tid = m.group(1)
        rest = m.group(2)
        if tid in tasks:
            errors.append('任务编号重复：%s' % tid)
        tasks[tid] = lineno
        if not TASK_TAG.search(rest) and not FLOW_TAG.search(text):
            errors.append('第 %d 行 %s 没有挂软件需求 ID（SSR…）或 R-xx、流程' % (lineno, tid))
    for tid, (lineno, tag_text) in table_tasks(heads).items():
        if tid in tasks:
            errors.append('任务编号重复：%s' % tid)
            continue
        tasks[tid] = lineno
        if not TASK_TAG.search(tag_text) and '流程' not in norm(tag_text):
            errors.append('第 %d 行 %s 没有挂软件需求 ID（SSR…）或 R-xx、流程' % (lineno, tid))
    if not tasks:
        errors.append('「任务」里没有任务表或任务行（表格列：任务｜批次｜类型｜归属｜覆盖需求｜状态；或 - [ ] T001 [B1] 标题 | SSR001）')

    # 任务卡
    cards = {}
    for h in heads:
        m = CARD_HEAD.match('#' * h['level'] + ' ' + h['title'])
        if not m:
            continue
        tid = m.group(1)
        if tid in cards:
            errors.append('任务卡重复：%s' % tid)
            continue
        cards[tid] = h
        fields = card_fields(h['body'])
        for name in CARD_FIELDS:
            value = field_value(fields, name)
            if value is None:
                if name in CARD_REQUIRED:
                    errors.append('%s 任务卡缺少字段：%s' % (tid, name))
                else:
                    warns.append('%s 任务卡缺少字段：%s' % (tid, name))
                continue
            if not value or (value.startswith('<') and value.endswith('>')):
                if name in CARD_REQUIRED:
                    errors.append('%s 任务卡字段为空：%s' % (tid, name))
                else:
                    warns.append('%s 任务卡字段为空：%s' % (tid, name))
    for tid in sorted(set(tasks) - set(cards)):
        errors.append('任务 %s 没有任务卡' % tid)
    for tid in sorted(set(cards) - set(tasks)):
        warns.append('任务卡 %s 没有对应任务表 / 任务行' % tid)

    # 覆盖映射
    cm = find_section(heads, '覆盖映射')
    if cm is not None:
        rows = table_rows(cm['body'])
        if not rows:
            errors.append('「覆盖映射」没有表格')
        else:
            idx_task = col_index(rows[0][1], '任务')
            idx_req = col_index(rows[0][1], 'REQ')
            for kw in ('软件需求', 'SSR'):
                if idx_req is None:
                    idx_req = col_index(rows[0][1], kw)
            if idx_task is None:
                errors.append('「覆盖映射」表头缺少「任务」列')
            if idx_req is None:
                errors.append('「覆盖映射」表头缺少「软件需求 ID / 异常」列')

    raw = open(path, encoding='utf-8').read()
    for ln, msg in lint_common.placeholder_issues(raw):
        errors.append('第 %d 行：%s' % (ln, msg))
    if not lint_common.has_role_header(raw, '实现者'):
        errors.append('缺少文档头：> 角色：实现者 ｜ 依据：…')
    warns.extend(lint_common.heading_order_warnings(
        raw, ['执行说明', '执行批次', '任务', '任务卡', '覆盖映射']))

    print('任务：%d ｜ 任务卡：%d' % (len(tasks), len(cards)))
    return report('check_implementation ' + path, errors, warns)


if __name__ == '__main__':
    sys.exit(main())

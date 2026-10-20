#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""规格结构检查（01-spec.md）。

检查 R -> US -> FR -> AC -> SC 链条的机械闭合：
- 产品根表有 ID / 类型 / 目标消费者 / 问题 / 使用价值 / 场景 / 现有替代 / 成功信号
- 每条用户故事引用存在的 R
- 每个主要 / 次要 R 至少被一条用户故事引用
- 每条用户故事有场景与结果、解决方向和 Given/When/Then 验收场景
- FR / SC 编号连续无重复
- 门 1 是否留下结论

只查机械事实；根是否成立、契约是否可验证由门 1 人工判断。
用法: python check_spec.py <项目>/SDD/01-spec.md
"""

import re
import sys

FENCE = re.compile(r'^\s*(?:\x60\x60\x60|~~~)')
ROOT_REF = re.compile(r'\*\*对应根\*\*[:：]\s*(.+)')
R_ID = re.compile(r'\bR\d+\b')


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
    print('OK   %s（%d 个警告）' % (tag, len(warns)))
    return 0


REQUIRED = ['产品根', '用户故事', '功能需求', '成功标准', '门 1', '修订记录']
RECOMMENDED = ['范围与目标', '非目标', '边界与异常', '假设与未决项', '交接给技术总监']


def table_cells(line):
    s = line.strip()
    if not s.startswith('|'):
        return None
    return [c.strip() for c in s.strip('|').split('|')]


def is_separator(cells):
    return all(re.fullmatch(r':?-{2,}:?', c.replace(' ', '')) for c in cells if c)


def col_index(header, *keywords):
    for i, h in enumerate(header):
        hn = norm(h)
        if all(k in hn for k in keywords):
            return i
    return None


def parse_roots(heads, errors, warns):
    sec = find_section(heads, '产品根')
    if sec is None:
        errors.append('缺少必需章节：产品根')
        return {}
    body_text = '\n'.join(t for _, t in sec['body'])
    if '产品根一句话' not in body_text:
        warns.append('「产品根」建议补一句「产品根一句话」摘要')

    rows = []
    for lineno, t in sec['body']:
        cells = table_cells(t)
        if not cells or is_separator(cells):
            continue
        rows.append((lineno, cells))
    if len(rows) < 2:
        errors.append('「产品根」没有有效表格')
        return {}

    header = rows[0][1]
    idx_id = col_index(header, 'ID')
    idx_type = col_index(header, '类型')
    idx_consumer = col_index(header, '消费者')
    idx_problem = col_index(header, '问题')
    idx_value = col_index(header, '价值')
    idx_scene = col_index(header, '场景')
    idx_alt = col_index(header, '替代')
    idx_success = col_index(header, '成功')
    required = [('ID', idx_id), ('类型', idx_type), ('目标消费者', idx_consumer),
                ('问题', idx_problem), ('使用价值', idx_value), ('场景', idx_scene),
                ('现有替代', idx_alt), ('成功信号', idx_success)]
    for label, idx in required:
        if idx is None:
            errors.append('「产品根」表头缺少列：' + label)
    if any(idx is None for _, idx in required):
        return {}

    roots = {}
    for lineno, cells in rows[1:]:
        if len(cells) <= max(idx_id, idx_type, idx_consumer, idx_problem, idx_value,
                             idx_scene, idx_alt, idx_success):
            errors.append('第 %d 行产品根表列数不足' % lineno)
            continue
        rid = cells[idx_id]
        kind_text = cells[idx_type]
        if '非目标' in kind_text:
            kind = '非目标'
        elif '次要' in kind_text:
            kind = '次要'
        elif '主要' in kind_text:
            kind = '主要'
        else:
            kind = ''
            warns.append('第 %d 行根类型不明确：%s（建议写主要 / 次要 / 非目标）' % (lineno, kind_text))
        if not re.fullmatch(r'[RN]\d+', rid):
            errors.append('第 %d 行根 ID 非法：%s（应为 R1、R2 或 N1 …）' % (lineno, rid))
            continue
        if rid.startswith('N') and kind != '非目标':
            errors.append('第 %d 行非目标 ID %s 的类型必须是「非目标」' % (lineno, rid))
        if rid.startswith('R') and kind == '非目标':
            errors.append('第 %d 行非目标根应使用 N 前缀：%s' % (lineno, rid))
        if rid in roots:
            errors.append('根 ID 重复：%s' % rid)
            continue
        if kind != '非目标':
            labels = [('目标消费者', idx_consumer), ('问题', idx_problem),
                      ('使用价值', idx_value), ('场景', idx_scene),
                      ('现有替代', idx_alt), ('成功信号', idx_success)]
            for label, idx in labels:
                if not cells[idx]:
                    errors.append('第 %d 行 %s 的「%s」为空' % (lineno, rid, label))
        roots[rid] = {'kind': kind, 'line': lineno, 'stories': set()}
    if not roots:
        errors.append('「产品根」没有有效根行')
    if not any(info['kind'] != '非目标' for info in roots.values()):
        errors.append('「产品根」至少需要一个主要或次要 R')
    return roots


def check_numbering(nums, label, errors):
    if not nums:
        errors.append('%s 一条都没有' % label)
        return
    if len(nums) != len(set(nums)):
        errors.append('%s 有重复编号' % label)
    missing = [n for n in range(1, max(nums) + 1) if n not in set(nums)]
    if missing:
        errors.append('%s 编号断号：缺 %s' % (
            label, ', '.join('%s-%03d' % (label, n) for n in missing)))


def main():
    if len(sys.argv) < 2:
        print(__doc__.strip())
        return 2
    path = sys.argv[1]
    pairs = read_unfenced(path)
    heads = sections(pairs)
    errors, warns = [], []

    for name in REQUIRED:
        if find_section(heads, name) is None:
            errors.append('缺少必需章节：' + name)
    for name in RECOMMENDED:
        if find_section(heads, name) is None:
            warns.append('建议补上章节：' + name)

    roots = parse_roots(heads, errors, warns)

    stories = [h for h in heads if re.match(r'^US\s*\d+', norm(h['title']))]
    if not stories:
        warns.append('没有找到用户故事（标题需形如 ### US1 <标题>）')
    for st in stories:
        body = '\n'.join(t for _, t in st['body'])
        m_story = re.match(r'^US\s*(\d+)', norm(st['title']))
        story_id = 'US' + m_story.group(1) if m_story else '?'
        m = ROOT_REF.search(body)
        if not m:
            errors.append('第 %d 行「%s」没有「对应根」引用' % (st['line'], st['title']))
        else:
            refs = R_ID.findall(m.group(1))
            if not refs:
                errors.append('第 %d 行「%s」没有引用 R ID' % (st['line'], st['title']))
            for rid in refs:
                if rid not in roots:
                    errors.append('第 %d 行「%s」引用了不存在的 %s' % (st['line'], st['title'], rid))
                else:
                    if roots[rid]['kind'] == '非目标':
                        errors.append('第 %d 行「%s」引用了非目标根 %s' % (st['line'], st['title'], rid))
                    roots[rid]['stories'].add(story_id)
        for field in ('场景与结果', '解决方向'):
            if field not in body:
                errors.append('第 %d 行「%s」缺少「%s」' % (st['line'], st['title'], field))
        if not re.search(r'\*\*Given\*\*', body, re.I) or not re.search(r'\*\*Then\*\*', body, re.I):
            errors.append('第 %d 行「%s」没有 Given/When/Then 验收场景' % (st['line'], st['title']))

    for rid, info in roots.items():
        if info['kind'] != '非目标' and not info['stories']:
            errors.append('根 %s 没有被任何用户故事引用' % rid)

    fr = []
    sec = find_section(heads, '功能需求')
    if sec:
        for _, t in sec['body']:
            m = re.match(r'^\s*[-*]?\s*\*\*(FR-\d{3})\*\*', t)
            if m:
                fr.append(int(m.group(1).split('-')[1]))
    check_numbering(fr, 'FR', errors)

    sc = []
    sec = find_section(heads, '成功标准')
    if sec:
        for _, t in sec['body']:
            m = re.match(r'^\s*[-*]?\s*\*\*(SC-\d{3})\*\*', t)
            if m:
                sc.append(int(m.group(1).split('-')[1]))
    check_numbering(sc, 'SC', errors)

    gate = find_section(heads, '门 1')
    if gate is None:
        pass
    else:
        concl = [t for _, t in gate['body'] if '结论' in t]
        if not concl:
            errors.append('门 1 小节里没有结论行')
        else:
            text = ' '.join(concl)
            if re.search(r'<[^>]*>', text):
                errors.append('门 1 结论仍是占位符：' + text.strip()[:60])
            elif 'reject' in text.lower():
                errors.append('门 1 结论是 reject，必须退回上游修完重跑')
            elif 'approve' in text.lower() and '裁决人' in text and '日期' in text:
                pass
            elif '待审' in text or '未审' in text:
                warns.append('门 1 结论仍是待审（尚未获得批准）')
            else:
                errors.append('门 1 结论格式不明，应为 approve ｜ 裁决人：… ｜ 日期：… 或 待审')

    return report('check_spec ' + path, errors, warns)


if __name__ == '__main__':
    sys.exit(main())

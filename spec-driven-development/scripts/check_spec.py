#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""规格结构检查（01-spec.md）。

只查机械事实：章节是否齐全、每条故事是否有验收场景、FR/SC 编号是否连续无重复、
门 1 是否留下结论。外部契约节可选，内容由门 1 人工判断；领域边界见 references/domains.md。
不判断需求写得好不好——那是人的事。

用法: python check_spec.py <项目>/SDD/01-spec.md
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
    """按归一化标题匹配（完全相等或前缀）。"""
    wanted = [norm(n) for n in names]
    for h in heads:
        t = norm(h['title'])
        for w in wanted:
            if t == w or t.startswith(w):
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

REQUIRED = ['用户故事', '功能需求', '成功标准', '门 1', '修订记录']
RECOMMENDED = ['范围与目标', '目标消费者', '非目标', '边界与异常', '假设与未决项', '交接给技术总监']


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

    stories = [h for h in heads if re.match(r'^US\s*\d+', norm(h['title']))]
    if not stories:
        warns.append('没有找到用户故事（标题需形如 ### US1 <标题>）')
    for st in stories:
        body = '\n'.join(t for _, t in st['body'])
        if not re.search(r'\*\*Given\*\*', body, re.I) or not re.search(r'\*\*Then\*\*', body, re.I):
            errors.append('第 %d 行「%s」没有 Given/When/Then 验收场景' % (st['line'], st['title']))

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

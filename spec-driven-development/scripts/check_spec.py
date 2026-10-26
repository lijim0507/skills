#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""规格结构检查（01-spec.md）。

检查 P -> US -> FR 链条的机械闭合：
- 产品定位表有 ID / 类型 / 消费者 / 场景 / 问题 / 价值
- 每条用户故事指向存在的 P，并至少指向一个 FR
- 每个主要 / 次要 P 至少被一条用户故事引用
- 每条新格式 FR 有来源、行为、验收；旧格式只提示迁移
- FR 编号连续无重复
- 门 1 是否留下结论

只查机械事实；定位是否成立、契约是否可验证由门 1 人工判断。
用法: python check_spec.py <项目>/SDD/01-spec.md
"""

import re
import sys
import lint_common

FENCE = re.compile(r'^\s*(?:\x60\x60\x60|~~~)')
POS_REF = re.compile(r'\*\*(?:定位|对应根)\*\*[:：]\s*(.+)')
POS_ID = re.compile(r'\b[PR]\d+\b')
FR_IN_TEXT = re.compile(r'\bFR-(\d{3})\b')
FR_DEF = re.compile(r'^\s*[-*]\s+\*\*(FR-\d{3})\*\*')
US_HEAD = re.compile(r'^US\s*(\d+)')


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


def has_label(body, *labels):
    compact = norm(body)
    return any(norm(label) in compact for label in labels)


def field_value(body, label):
    m = re.search(r'\*\*' + re.escape(label) + r'\*\*[:：]\s*(.+)', body)
    return m.group(1).strip() if m else ''


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


def parse_positioning(heads, errors, warns):
    sec = find_section(heads, '产品定位', '产品根')
    if sec is None:
        errors.append('缺少必需章节：产品定位')
        return {}

    body_text = '\n'.join(t for _, t in sec['body'])
    if not re.search(r'\*\*成功信号\*\*[:：]\s*\S+', body_text):
        warns.append('「产品定位」建议补一行「成功信号」')

    rows = []
    for lineno, t in sec['body']:
        cells = table_cells(t)
        if not cells or is_separator(cells):
            continue
        rows.append((lineno, cells))
    if len(rows) < 2:
        errors.append('「产品定位」没有有效表格')
        return {}

    header = rows[0][1]
    idx_id = col_index(header, 'ID')
    idx_type = col_index(header, '类型')
    idx_consumer = col_index(header, '消费者')
    idx_scene = col_index(header, '场景')
    idx_problem = col_index(header, '问题')
    idx_value = col_index(header, '价值')
    required = [('ID', idx_id), ('类型', idx_type), ('消费者', idx_consumer),
                ('场景', idx_scene), ('问题', idx_problem), ('价值', idx_value)]
    for label, idx in required:
        if idx is None:
            errors.append('「产品定位」表头缺少列：' + label)
    if any(idx is None for _, idx in required):
        return {}

    roots = {}
    for lineno, cells in rows[1:]:
        if len(cells) <= max(idx_id, idx_type, idx_consumer, idx_scene, idx_problem, idx_value):
            errors.append('第 %d 行产品定位表列数不足' % lineno)
            continue
        rid = cells[idx_id]
        kind_text = cells[idx_type]
        if ('不服务' in kind_text) or ('非目标' in kind_text):
            kind = '不服务'
        elif '次要' in kind_text:
            kind = '次要'
        elif '主要' in kind_text:
            kind = '主要'
        else:
            kind = ''
            warns.append('第 %d 行类型不明确：%s（建议写主要 / 次要 / 不服务）' % (lineno, kind_text))
        if not re.fullmatch(r'[RPN]\d+', rid):
            errors.append('第 %d 行定位 ID 非法：%s（应为 P1、P2 或 N1 …）' % (lineno, rid))
            continue
        if rid.startswith('N') and kind != '不服务':
            errors.append('第 %d 行不服务 ID %s 的类型必须是「不服务」' % (lineno, rid))
        if rid.startswith(('P', 'R')) and kind == '不服务':
            errors.append('第 %d 行不服务项应使用 N 前缀：%s' % (lineno, rid))
        if rid in roots:
            errors.append('定位 ID 重复：%s' % rid)
            continue
        if kind != '不服务':
            labels = [('消费者', idx_consumer), ('场景', idx_scene),
                      ('问题', idx_problem), ('价值', idx_value)]
            for label, idx in labels:
                if not cells[idx]:
                    errors.append('第 %d 行 %s 的「%s」为空' % (lineno, rid, label))
        roots[rid] = {'kind': kind, 'line': lineno, 'stories': set()}
    if not roots:
        errors.append('「产品定位」没有有效定位行')
    if not any(info['kind'] != '不服务' for info in roots.values()):
        errors.append('「产品定位」至少需要一个主要或次要 P')
    return roots


def parse_stories(heads, roots, errors):
    stories = {}
    for h in heads:
        m = US_HEAD.match(norm(h['title']))
        if not m:
            continue
        story_id = int(m.group(1))
        body = '\n'.join(t for _, t in h['body'])
        m_ref = POS_REF.search(body)
        if not m_ref:
            errors.append('第 %d 行「%s」没有「定位」引用' % (h['line'], h['title']))
        else:
            refs = POS_ID.findall(m_ref.group(1))
            if not refs:
                errors.append('第 %d 行「%s」没有引用 P ID' % (h['line'], h['title']))
            for rid in refs:
                if rid not in roots:
                    errors.append('第 %d 行「%s」引用了不存在的 %s' % (h['line'], h['title'], rid))
                elif roots[rid]['kind'] == '不服务':
                    errors.append('第 %d 行「%s」引用了不服务项 %s' % (h['line'], h['title'], rid))
                else:
                    roots[rid]['stories'].add(story_id)

        new_style = has_label(body, '消费者/场景', '消费者／场景')
        old_style = has_label(body, '场景与结果') and has_label(body, '解决方向')
        if new_style:
            for label in ('想要', '结果', '对应功能'):
                if not has_label(body, label):
                    errors.append('第 %d 行「%s」缺少「%s」' % (h['line'], h['title'], label))
        elif old_style:
            if not has_label(body, '覆盖需求') and not FR_IN_TEXT.search(body):
                errors.append('第 %d 行「%s」没有「覆盖需求」或 FR 引用' % (h['line'], h['title']))
        else:
            errors.append('第 %d 行「%s」缺少「消费者/场景 + 想要/结果」' % (h['line'], h['title']))

        frs = [int(x) for x in FR_IN_TEXT.findall(body)]
        if not frs:
            errors.append('第 %d 行「%s」没有指向任何 FR' % (h['line'], h['title']))
        stories[story_id] = {'line': h['line'], 'frs': frs}
    if not stories:
        errors.append('没有找到用户故事（标题需形如 ### US1 <标题>）')
    return stories


def parse_frs(heads, stories, errors, warns):
    sec = find_section(heads, '功能需求')
    if sec is None:
        errors.append('缺少必需章节：功能需求')
        return {}

    blocks = []
    current = None
    for lineno, t in sec['body']:
        m = FR_DEF.match(t)
        if m:
            current = {'id': int(m.group(1).split('-')[1]), 'line': lineno, 'body': []}
            blocks.append(current)
        elif current is not None:
            if re.match(r'^#{1,6}\s+', t):
                current = None
            else:
                current['body'].append((lineno, t))

    fr_defs = {}
    old_count = 0
    for block in blocks:
        n = block['id']
        if n in fr_defs:
            errors.append('FR 编号重复：FR-%03d' % n)
            continue
        text = '\n'.join(t for _, t in block['body'])
        fresh = ('**来源**' in text) or any(t.strip().startswith('- **') for _, t in block['body'])
        if fresh:
            source = field_value(text, '来源')
            if not source:
                errors.append('FR-%03d 缺少「来源」' % n)
            else:
                us_refs = [int(x) for x in re.findall(r'US\s*(\d+)', source)]
                if not us_refs:
                    errors.append('FR-%03d 的来源没有引用 US' % n)
                for us in us_refs:
                    if us not in stories:
                        errors.append('FR-%03d 引用了不存在的 US%d' % (n, us))
            for label in ('行为', '验收'):
                if not has_label(text, label):
                    errors.append('FR-%03d 缺少「%s」' % (n, label))
            if not has_label(text, '输入/输出'):
                warns.append('FR-%03d 建议补「输入 / 输出」' % n)
            if not has_label(text, '规则与边界'):
                warns.append('FR-%03d 建议补「规则与边界」' % n)
            if not ('Given' in text and 'Then' in text):
                errors.append('FR-%03d 的验收缺少 Given/Then' % n)
        else:
            old_count += 1
        fr_defs[n] = {'line': block['line']}

    if old_count:
        warns.append('%d 条 FR 使用旧格式，建议补来源 / 行为 / 验收' % old_count)

    check_numbering(sorted(fr_defs), 'FR', errors)

    for story_id, info in stories.items():
        for fr in info['frs']:
            if fr not in fr_defs:
                errors.append('US%d 引用了不存在的 FR-%03d' % (story_id, fr))
    return fr_defs


def main():
    if len(sys.argv) < 2:
        print(__doc__.strip())
        return 2
    path = sys.argv[1]
    pairs = read_unfenced(path)
    heads = sections(pairs)
    errors, warns = [], []

    if find_section(heads, '产品定位', '产品根') is None:
        errors.append('缺少必需章节：产品定位')
    for name in ('用户故事', '功能需求', '门 1', '修订记录'):
        if find_section(heads, name) is None:
            errors.append('缺少必需章节：' + name)
    if find_section(heads, '交接给技术总监') is None:
        warns.append('建议补上章节：交接给技术总监')
    if find_section(heads, '未决项', '假设与未决项') is None:
        warns.append('建议补上章节：未决项')

    roots = parse_positioning(heads, errors, warns)
    stories = parse_stories(heads, roots, errors)
    fr_defs = parse_frs(heads, stories, errors, warns)

    for rid, info in roots.items():
        if info['kind'] != '不服务' and not info['stories']:
            errors.append('定位 %s 没有被任何用户故事引用' % rid)

    gate = find_section(heads, '门 1')
    if gate is not None:
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

    raw = open(path, encoding='utf-8').read()
    for ln, msg in lint_common.placeholder_issues(raw):
        errors.append('第 %d 行：%s' % (ln, msg))
    for m in re.finditer(r'FR-(\d{3})', raw):
        if int(m.group(1)) not in fr_defs:
            errors.append('正文引用了不存在的 FR-%s' % m.group(1))
    if not lint_common.has_role_header(raw, '产品经理'):
        errors.append('缺少文档头：> 角色：产品经理 ｜ 依据：…')
    warns.extend(lint_common.heading_order_warnings(raw, ['产品定位', '用户故事', '功能需求', '未决项', '门 1', '交接给技术总监', '修订记录']))
    return report('check_spec ' + path, errors, warns)


if __name__ == '__main__':
    sys.exit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""任务检查（03-tasks.md）。

只查机械事实：章节是否齐全、任务行格式与编号、每条任务是否挂了 FR 或标了「流程」、
任务状态统计、任务卡字段、开工前检查的勾选统计。

任务卡是给执行者的工单；简单任务可以只用索引行，非平凡任务应有卡。
卡里缺「目标 / 范围 / 输入 / 产出 / 完成判据 / 验证 / 依赖」会报错。

用法: python check_tasks.py <项目>/SDD/03-tasks.md
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

TASK = re.compile(r'^\s*[-*]\s+\[([ xX~])\]\s*T(\d{3})\b')
CHK = re.compile(r'^\s*[-*]\s+\[([ xX])\]\s*CHK(\d{3})\b')
CARD = re.compile(r'^T(\d{3})\b')
CARD_REQUIRED = [
    ('执行者', '执行者'),
    ('目标', '目标'),
    ('范围', '范围'),
    ('输入', '输入'),
    ('产出', '产出'),
    ('完成判据（DoD）', '完成判据'),
    ('验证', '验证'),
    ('依赖', '依赖'),
]
REQUIRED = ['任务', '覆盖映射', '开工前检查', '修订记录']
RECOMMENDED = ['任务分配说明', '执行批次', '任务卡', 'analyze 交叉检查', '收敛追加']


def collect_cards(heads, errors):
    """返回 {任务号: [卡正文行]}；没有「任务卡」节返回 None。"""
    sec = find_section(heads, '任务卡')
    if sec is None:
        return None
    cards = {}
    start = heads.index(sec)
    current = None
    for h in heads[start + 1:]:
        if h['level'] <= 2:
            break
        if h['level'] == 3:
            m = CARD.match(h['title'])
            if m:
                current = int(m.group(1))
                if current in cards:
                    errors.append('任务卡 T%03d 重复' % current)
                cards.setdefault(current, []).extend(t for _, t in h['body'])
            else:
                current = None
        elif current is not None:
            cards[current].extend(t for _, t in h['body'])
    return cards


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

    nums, done, todo, void, unnamed, flow = [], [], [], [], [], set()
    for lineno, t in pairs:
        m = TASK.match(t)
        if not m:
            continue
        status, num = m.group(1), int(m.group(2))
        nums.append(num)
        if status in 'xX':
            done.append(num)
        elif status == '~':
            void.append(num)
        else:
            todo.append(num)
        line_norm = norm(t)
        if '|流程' in line_norm:
            flow.add(num)
        if not re.search(r'FR-\d{3}', t) and '|流程' not in line_norm:
            unnamed.append('第 %d 行 T%03d 既没挂 FR 也没标 | 流程' % (lineno, num))

    if not nums:
        errors.append('一条任务行都没有（格式必须是 - [ ] T001 …）')
    if len(nums) != len(set(nums)):
        errors.append('任务编号有重复')
    if nums != sorted(nums):
        warns.append('任务编号没有按升序排列')
    errors.extend(unnamed[:5])
    if len(unnamed) > 5:
        errors.append('还有 %d 条任务没挂 FR / 流程标记' % (len(unnamed) - 5))

    cards = collect_cards(heads, errors)
    card_count = 0
    if cards is None:
        warns.append('没有「任务卡」节：简单任务可只用清单；非平凡任务应补任务卡，否则不可独立分配')
    else:
        card_count = len(cards)
        for num in sorted(set(cards) - set(nums)):
            errors.append('任务卡 T%03d 没有对应的任务索引行' % num)
        for num in nums:
            if num not in cards:
                if num not in flow and num not in void:
                    warns.append('任务 T%03d 没有任务卡（简单任务可只用索引；非平凡任务应补卡）' % num)
                continue
            body = '\n'.join(cards[num])
            for label, key in CARD_REQUIRED:
                if key not in body:
                    errors.append('任务卡 T%03d 缺少「%s」' % (num, label))
        if card_count == 0:
            warns.append('「任务卡」节里没有任务卡')

    chk_total, chk_checked = 0, 0
    chk_lines = []
    for _, t in pairs:
        m = CHK.match(t)
        if not m:
            continue
        chk_total += 1
        chk_lines.append(t)
        if m.group(1) in 'xX':
            chk_checked += 1
    if chk_total == 0:
        warns.append('没有找到开工前检查项（格式必须是 - [ ] CHK001 …）')
    else:
        if chk_checked < chk_total:
            warns.append('开工前检查未全勾：Checked %d / Total %d —— implement 前必须停下询问'
                         % (chk_checked, chk_total))
        chk_text = '\n'.join(chk_lines)
        for keyword in ('任务卡', '完成判据', '可独立分配'):
            if keyword not in chk_text:
                warns.append('开工前检查建议包含「%s」相关项' % keyword)

    print('任务：共 %d ｜ 未完成 %d ｜ 已完成 %d ｜ 已作废 %d'
          % (len(nums), len(todo), len(done), len(void)))
    print('任务卡：%d ｜ 开工前检查：Checked %d / Total %d'
          % (card_count, chk_checked, chk_total))
    return report('check_tasks ' + path, errors, warns)


if __name__ == '__main__':
    sys.exit(main())

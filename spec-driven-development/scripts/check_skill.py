#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""技能体积与链接检查。

预算：SKILL.md <= 8 KB；roles/*.md <= 2 KB；references/*.md <= 4 KB（_archive 不计）。
另外检查 SKILL.md 里引用的路径是否存在。

用法: python check_skill.py [技能目录]
"""
import glob
import os
import re
import sys

BUDGETS = [
    ('SKILL.md', 8 * 1024, '入口'),
    ('roles', 2 * 1024, '角色页'),
    ('references', 4 * 1024, '参考页'),
]
LINK = re.compile(r'(?:roles|references|templates|scripts)/[A-Za-z0-9._*/-]+')


def main():
    base = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    errors, warns = [], []
    skill = os.path.join(base, 'SKILL.md')
    if not os.path.isfile(skill):
        print('[ERROR] 找不到 SKILL.md')
        return 1

    def check_file(path, limit, label):
        size = os.path.getsize(path)
        name = os.path.relpath(path, base)
        if size > limit:
            errors.append('%s %s 为 %d B，超出预算 %d B' % (label, name, size, limit))

    check_file(skill, BUDGETS[0][1], BUDGETS[0][2])
    for folder, limit, label in BUDGETS[1:]:
        for path in sorted(glob.glob(os.path.join(base, folder, '*.md'))):
            check_file(path, limit, label)

    text = open(skill, encoding='utf-8').read()
    seen = set()
    for raw in LINK.findall(text):
        target = raw.rstrip('.,;:)]')
        if target in seen:
            continue
        seen.add(target)
        full = os.path.join(base, target.replace('/', os.sep))
        if not os.path.exists(full) and not glob.glob(full):
            errors.append('SKILL.md 引用了不存在的路径：' + target)

    for path in sorted(glob.glob(os.path.join(base, 'roles', '*.md'))):
        rel = 'roles/' + os.path.basename(path)
        if rel not in seen:
            warns.append('角色页未被 SKILL.md 引用：' + rel)

    for e in errors:
        print('[ERROR] ' + e)
    for w in warns:
        print('[WARN]  ' + w)
    print('体积：SKILL %d B ｜ roles %d 个 ｜ references %d 个' % (
        os.path.getsize(skill),
        len(glob.glob(os.path.join(base, 'roles', '*.md'))),
        len(glob.glob(os.path.join(base, 'references', '*.md')))))
    if errors:
        print('FAIL check_skill %s：%d 个错误，%d 个警告' % (base, len(errors), len(warns)))
        return 1
    print('结构检查通过 · 语义未验证  check_skill %s（%d 个警告）' % (base, len(warns)))
    return 0


if __name__ == '__main__':
    sys.exit(main())

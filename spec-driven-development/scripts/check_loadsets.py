#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""装载集预算检查。

用法:
    python check_loadsets.py [技能目录] [load_sets.json]

做三件事:
1. 每个装载集求字节和，超预算报错；
2. cumulative 集合连同 include 上游一起算；
3. 扫 SKILL.md 与 workflows/main-flow.md 的链接，发现未登记文件告警。

只读，不改文件。est_tokens 为估算值（中文约 3 B/token），不参与判定。
"""
import glob
import json
import os
import re
import sys

LINK = re.compile(r'\[[^\]]*\]\(([^)#]+)')
SKIP_PREFIX = ('http://', 'https://', 'mailto:', 'SDD/', '<')


def read_sets(path):
    with open(path, encoding='utf-8') as fh:
        return json.load(fh)


def files_of(name, sets):
    item = sets.get(name) or {}
    return list(item.get('files') or [])


def walk(name, sets, stack=()):
    """返回 (文件列表, 缺失列表)；include 递归展开。"""
    if name in stack:
        return [], ['循环 include: ' + name]
    item = sets.get(name)
    if not isinstance(item, dict):
        return [], ['未定义的装载集: ' + name]
    files, missing = list(item.get('files') or []), []
    for parent in item.get('include') or []:
        sub_files, sub_missing = walk(parent, sets, stack + (name,))
        files += sub_files
        missing += sub_missing
    return files, missing


def size_of(base, rel):
    full = os.path.join(base, rel.replace('/', os.sep))
    if os.path.isfile(full):
        return os.path.getsize(full)
    hits = glob.glob(full)
    if hits:
        return sum(os.path.getsize(p) for p in hits)
    return None


def registered(sets):
    known = set()
    for name, item in sets.items():
        if not isinstance(item, dict) or name in ('schema_version', 'note'):
            continue
        known.update(item.get('files') or [])
    return known


def scan_links(base, sets):
    known = registered(sets)
    warns = []
    for doc in ('SKILL.md', os.path.join('workflows', 'main-flow.md')):
        path = os.path.join(base, doc)
        if not os.path.isfile(path):
            continue
        with open(path, encoding='utf-8-sig') as fh:
            text = fh.read()
        for raw in LINK.findall(text):
            target = raw.strip().rstrip('.,;:')
            if not target or target.startswith(SKIP_PREFIX) or '*' in target:
                continue
            target = target.replace('\\', '/')
            if '(' in target or ' ' in target or target.endswith('/'):
                continue
            if not target.startswith(('roles/', 'references/', 'templates/')):
                continue
            if target not in known:
                warns.append('%s 引用了未登记文件: %s' % (doc, target))
    return warns


def main():
    base = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sets_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(base, 'scripts', 'load_sets.json')
    sets = read_sets(sets_path)

    errors, warns = [], []
    print('%-22s %9s %10s %9s  %s' % ('装载集', 'bytes', 'est_tokens', 'budget', '状态'))
    for name, item in sets.items():
        if not isinstance(item, dict) or name in ('schema_version', 'note'):
            continue
        files, missing = walk(name, sets)
        if missing:
            errors += missing
        used = 0
        for rel in files:
            size = size_of(base, rel)
            if size is None:
                errors.append('%s 缺少文件: %s' % (name, rel))
                continue
            used += size
        budget = int(item.get('max_bytes') or 0)
        status = 'OK'
        if budget and used > budget:
            status = 'OVER +%d' % (used - budget)
            errors.append('%s 超预算: %d > %d B' % (name, used, budget))
        print('%-22s %9d %10d %9d  %s' % (name, used, round(used / 3), budget, status))

    warns += scan_links(base, sets)

    for item in warns:
        print('[WARN]  ' + item)
    for item in errors:
        print('[ERROR] ' + item)
    print('结构检查通过 · 语义未验证  check_loadsets（%d 个错误，%d 个警告）'
          % (len(errors), len(warns)))
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())

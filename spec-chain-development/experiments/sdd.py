#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SDD 角色边界守卫（旧版原型，已冻结）。

把"调用头"从回执变成许可证：
    open   按角色写 state.json，并给整棵树打基线哈希
    guard  写入前检查目标路径是否在角色的写白名单内（越界退出码 1）
    check  收盘比对基线：谁改了哪些文件、有没有越界
    status 看当前角色和许可证

用法:
    python sdd.py open   --root <项目根> --role 01
    python sdd.py guard  --root <项目根> SDD/02-plan.md
    python sdd.py check  --root <项目根>
    python sdd.py status --root <项目根>

只读判断，不改被检文件；唯一的写操作是 <root>/SDD/.sdd/state.json。
"""
import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone, timedelta

SKIP_DIRS = {'.git', '.sdd', 'node_modules', '__pycache__', '.venv', 'venv'}
STATE_REL = os.path.join('SDD', '.sdd', 'state.json')
TZ = timezone(timedelta(hours=8))

# 角色许可证：write 为该角色唯一允许改动的路径（glob，相对 root）。
# 旧版角色集里有四处权限是小节级 / 行级的，文件级白名单表达不了，先如实标在 note 里。
ROLES = {
    '00': dict(
        name='裁决人', stage='S2 / S4 / S9',
        write=[],
        read=['SDD/01-spec.md', 'SDD/02-plan.md', 'SDD/04-converge.md', 'SDD/.sdd/state.json'],
        stop='门 1 / 门 2 / 验收',
        forbid='不写 01/02/03 正文；不代签；不读实现细节',
        note='需改"门结论"小节 → 本原型不支持小节级权限',
    ),
    '01': dict(
        name='产品经理', stage='S1',
        write=['SDD/01-spec.md'],
        read=['SDD/00-constitution.md', 'SDD/01-spec.md'],
        stop='门 1',
        forbid='不写 02/03/代码；不替 02 做技术选型；不自己写 approve',
        note='',
    ),
    '02': dict(
        name='技术总监', stage='S3',
        write=['SDD/02-plan.md', 'SDD/02-plan-*.md'],
        read=['SDD/00-constitution.md', 'SDD/01-spec.md', 'SDD/02-plan*.md'],
        stop='门 2',
        forbid='不写 01/03/代码；不改需求；不悄悄降级',
        note='',
    ),
    '03': dict(
        name='任务负责人', stage='S5 / S8',
        write=['SDD/03-tasks.md', 'SDD/04-converge.md'],
        read=['SDD/00-constitution.md', 'SDD/01-spec.md', 'SDD/02-plan*.md', 'SDD/03-tasks.md'],
        stop='开工检查 / 收敛结论',
        forbid='不写 01/02/代码；不改架构；不把没想清的问题塞进任务卡',
        note='04-converge 的"验收节"归 06，与 06 共写同一文件 → 需拆文件',
    ),
    '04': dict(
        name='执行者', stage='S7',
        write=['SDD/03-tasks.md', 'src/**', 'tests/**'],
        read=['SDD/03-tasks.md'],
        stop='任务完成 / blocked',
        forbid='不改 01/02/03 正文；不超出任务卡范围；不自己补 spec',
        note='03-tasks 只允许勾状态（[ ] ↔ [x]），不允许改任务定义 → 需行级权限',
    ),
    '05': dict(
        name='评审者', stage='S6',
        write=[],
        read=['SDD/01-spec.md', 'SDD/02-plan.md', 'SDD/03-tasks.md'],
        stop='评审完成',
        forbid='不写正文；不只写"未发现问题"；不替裁决人签字',
        note='需改"评审记录 / analyze"小节 → 本原型不支持小节级权限',
    ),
    '06': dict(
        name='验收人', stage='S9',
        write=['SDD/04-converge.md'],
        read=['SDD/01-spec.md', 'SDD/03-tasks.md', 'SDD/04-converge.md'],
        stop='验收',
        forbid='不写 01/02/03 正文；不替执行者补证据；不签未跑过的场景',
        note='只该写 04 的"验收节"，与 03 共写同一文件 → 需拆文件或小节级权限',
    ),
}

ALIASES = {
    'adjudicator': '00', 'pm': '01', 'architect': '02', 'owner': '03',
    'implementer': '04', 'reviewer': '05', 'acceptor': '06',
}


def norm_role(raw):
    r = str(raw).strip().lower()
    if r in ROLES:
        return r
    if r in ALIASES:
        return ALIASES[r]
    if r.zfill(2) in ROLES:
        return r.zfill(2)
    raise SystemExit('[ERROR] 未知角色：%s（可用 00–06 或 %s）' % (raw, ', '.join(ALIASES)))


def now():
    return datetime.now(TZ).strftime('%Y-%m-%dT%H:%M:%S%z')


def state_path(root):
    return os.path.join(root, STATE_REL)


def load_state(root):
    p = state_path(root)
    if not os.path.isfile(p):
        raise SystemExit('[ERROR] 没有 SDD/.sdd/state.json：先跑 open --role <00-06>')
    with open(p, encoding='utf-8') as fh:
        return json.load(fh)


def save_state(root, state):
    p = state_path(root)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8') as fh:
        json.dump(state, fh, ensure_ascii=False, indent=2)
        fh.write('\n')


def rel_posix(root, full):
    return os.path.relpath(full, root).replace(os.sep, '/')


def snapshot(root):
    """返回 {relpath: sha256}，用于判断"谁改了什么"。"""
    out = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            full = os.path.join(dirpath, fn)
            rel = rel_posix(root, full)
            try:
                with open(full, 'rb') as fh:
                    out[rel] = hashlib.sha256(fh.read()).hexdigest()
            except OSError:
                out[rel] = '<unreadable>'
    return out


def match_any(path, globs):
    from fnmatch import fnmatch
    return any(fnmatch(path, g) for g in globs)


def cmd_open(args):
    root = os.path.abspath(args.root)
    role = norm_role(args.role)
    spec = ROLES[role]
    state = {
        'schema': 1,
        'role': role,
        'role_name': spec['name'],
        'stage': args.stage or spec['stage'],
        'write': spec['write'],
        'read': spec['read'],
        'stop': spec['stop'],
        'forbid': spec['forbid'],
        'note': spec['note'],
        'root': root,
        'opened_at': now(),
        'gate': {'approved_by': None, 'approved_at': None, 'quote': None},
        'baseline': snapshot(root),
    }
    save_state(root, state)

    print('本次角色：%s %s' % (role, spec['name']))
    print('本次阶段：%s' % state['stage'])
    print('只读：%s' % ('、'.join(spec['read']) or '—'))
    print('只写：%s' % ('、'.join(spec['write']) or '【无】本角色不改文件（见备注）'))
    print('停点：%s' % spec['stop'])
    print('禁止：%s' % spec['forbid'])
    if spec['note']:
        print('备注：%s' % spec['note'])
    print()
    print('许可证已落盘：%s（基线 %d 个文件）' % (STATE_REL, len(state['baseline'])))
    print('下一步：用户确认后动笔；收工跑 check。')
    return 0


def cmd_guard(args):
    root = os.path.abspath(args.root)
    state = load_state(root)
    bad = []
    for target in args.paths:
        rel = os.path.relpath(os.path.abspath(os.path.join(root, target)), root).replace(os.sep, '/')
        if match_any(rel, state['write']):
            print('[ALLOW] %s' % rel)
        else:
            bad.append(rel)
            print('[DENY]  %s —— %s %s 的写白名单里没有它' % (rel, state['role'], state['role_name']))
    if bad:
        print()
        print('越界：%d 个。停手，按角色卡退回规则处理；不要"顺手"写。' % len(bad))
        print('允许写：%s' % ('、'.join(state['write']) or '【无】'))
        return 1
    return 0


def cmd_check(args):
    root = os.path.abspath(args.root)
    state = load_state(root)
    before = state['baseline']
    after = snapshot(root)

    changed = []
    for rel in sorted(set(before) | set(after)):
        if rel.startswith('SDD/.sdd/'):
            continue
        b, a = before.get(rel), after.get(rel)
        if b == a:
            continue
        kind = 'A' if b is None else ('D' if a is None else 'M')
        changed.append((kind, rel))

    print('角色：%s %s ｜ 阶段：%s ｜ 开工：%s'
          % (state['role'], state['role_name'], state['stage'], state['opened_at']))
    if not changed:
        print('改动：0 个文件。')
    else:
        print('改动：%d 个文件' % len(changed))
    violations = []
    for kind, rel in changed:
        ok = match_any(rel, state['write'])
        print('  %s %-34s %s' % (kind, rel, 'OK' if ok else '越界'))
        if not ok:
            violations.append(rel)

    gate = state.get('gate') or {}
    print()
    if gate.get('approved_by'):
        print('门：已批准 by %s @ %s' % (gate['approved_by'], gate['approved_at']))
    else:
        print('门：未批准（%s）—— 未批准不得开工' % state['stop'])

    if violations:
        print()
        print('FAIL 越界 %d 个：%s' % (len(violations), '、'.join(violations)))
        print('允许写：%s' % ('、'.join(state['write']) or '【无】'))
        return 1
    print()
    print('边界检查通过 · 语义未验证（只证明改动落在该角色的白名单内）')
    return 0


def cmd_status(args):
    root = os.path.abspath(args.root)
    state = load_state(root)
    print('角色 %s %s ｜ 阶段 %s ｜ 开工 %s' % (
        state['role'], state['role_name'], state['stage'], state['opened_at']))
    print('只写：%s' % ('、'.join(state['write']) or '【无】'))
    print('停点：%s' % state['stop'])
    gate = state.get('gate') or {}
    print('门：%s' % ('已批准 by %s' % gate['approved_by'] if gate.get('approved_by') else '未批准'))
    return 0


def cmd_approve(args):
    """由人批准：记录谁批的、批的是哪句原话。agent 代签需伪造具体原话。"""
    root = os.path.abspath(args.root)
    state = load_state(root)
    state['gate'] = {
        'approved_by': args.by,
        'approved_at': now(),
        'quote': args.quote,
        'version': args.version,
    }
    save_state(root, state)
    print('已记录：%s 批准 %s（版本 %s）' % (args.by, state['stop'], args.version))
    print('原话：%s' % args.quote)
    return 0


def main():
    ap = argparse.ArgumentParser(description='SDD 角色边界守卫')
    sub = ap.add_subparsers(dest='cmd', required=True)

    p = sub.add_parser('open', help='按角色开工，落盘许可证')
    p.add_argument('--root', default='.', help='项目根（含 SDD/）')
    p.add_argument('--role', required=True, help='00–06 或角色别名')
    p.add_argument('--stage', default='', help='覆盖默认阶段')
    p.set_defaults(func=cmd_open)

    p = sub.add_parser('guard', help='写入前检查目标路径')
    p.add_argument('--root', default='.', help='项目根')
    p.add_argument('paths', nargs='+', help='要写的文件（相对 root）')
    p.set_defaults(func=cmd_guard)

    p = sub.add_parser('check', help='收盘比对基线，判越界')
    p.add_argument('--root', default='.', help='项目根')
    p.set_defaults(func=cmd_check)

    p = sub.add_parser('status', help='看当前许可证')
    p.add_argument('--root', default='.', help='项目根')
    p.set_defaults(func=cmd_status)

    p = sub.add_parser('approve', help='人批准门（记录原话）')
    p.add_argument('--root', default='.', help='项目根')
    p.add_argument('--by', required=True, help='批准人')
    p.add_argument('--quote', required=True, help='批准人的原话')
    p.add_argument('--version', default='r1', help='被批准的文档版本')
    p.set_defaults(func=cmd_approve)

    args = ap.parse_args()
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())

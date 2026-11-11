# -*- coding: utf-8 -*-
"""SDD 共享 lint 辅助：只做机械检查，不做语义判断。"""
import re

PLACEHOLDERS = ('待填', 'TODO', '<…>')


def placeholder_issues(text):
    out = []
    for i, line in enumerate(text.splitlines(), 1):
        for token in PLACEHOLDERS:
            if token in line:
                out.append((i, '占位符 %s 未清理' % token))
    return out


def has_role_header(text, keyword):
    for line in text.splitlines()[:40]:
        if '角色：' in line and keyword in line:
            return True
    return False


def strip_number(title):
    """去掉标题开头的章节号：`5.1 架构摘要（软件描述）` → `架构摘要（软件描述）`。"""
    return re.sub(r'^\d+(?:\.\d+)*\s*', '', title.strip())


def heading_order_warnings(text, order):
    heads = []
    for line in text.splitlines():
        m = re.match(r'^##\s+(.+?)\s*$', line)
        if not m:
            continue
        title = m.group(1).strip()
        plain = strip_number(title)
        for idx, name in enumerate(order):
            if plain.startswith(name):
                heads.append((idx, title))
                break
    idxs = [i for i, _ in heads]
    if idxs != sorted(idxs):
        return ['章节顺序与模板不一致：' + ' → '.join(t for _, t in heads)]
    return []


def empty_field_issues(text):
    out = []
    for i, line in enumerate(text.splitlines(), 1):
        if re.match(r'^-\s+\*\*[^*]+\*\*：\s*$', line.strip()):
            out.append((i, '字段值为空'))
    return out

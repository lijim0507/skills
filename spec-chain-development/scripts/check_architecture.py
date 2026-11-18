#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""架构检查（02-architecture.md，SWE.2 结构）。

只查机械事实：章节是否齐全、模块清单表头、模块名唯一、依赖环、模块契约节覆盖、
每个模块的「覆盖 REQ」、公开接口关键字、文档头与章节顺序。
模块粒度好不好由人确认前判断。

用法: python check_architecture.py <项目>/SDD
"""

import os
import re
import sys
import lint_common

FENCE = re.compile(r'^\s*(?:\x60\x60\x60|~~~)')
REQ_ID = r'REQ(?:-[A-Za-z0-9]+)+'
REQ_DEF = re.compile(r'^\s*\*\*\s*\[?(' + REQ_ID + r')\]?\s*(.*?)\s*\*\*\s*$')
REQ_IN_TEXT = re.compile(r'\b(' + REQ_ID + r')\b')
ROLE_HINTS = {
    'ui', 'repository', 'service', 'controller', 'view', 'model',
    'domain', 'data', 'infrastructure', 'presentation', 'application',
    'api', 'db', 'database', 'frontend', 'backend', 'adapter', 'gateway',
    'usecase', 'store',
}


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
    print('未覆盖：模板符合度、角色边界、架构可行性')
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


def is_placeholder(s):
    s = s.strip()
    return not s or (s.startswith('<') and s.endswith('>'))


def parse_deps(cell):
    cell = clean_cell(cell)
    if not cell or cell in ('-', '—', '无', 'none', 'None'):
        return []
    parts = re.split(r'[,，、;；]', cell)
    return [clean_cell(p) for p in parts
            if clean_cell(p) and clean_cell(p) not in ('-', '—', '无', 'none', 'None')]


def find_cycle(graph):
    color = {n: 0 for n in graph}
    stack = []

    def dfs(n):
        color[n] = 1
        stack.append(n)
        for m in graph.get(n, []):
            if m not in graph:
                continue
            if color[m] == 1:
                i = stack.index(m)
                return stack[i:] + [m]
            if color[m] == 0:
                cyc = dfs(m)
                if cyc:
                    return cyc
        stack.pop()
        color[n] = 2

    for n in graph:
        if color[n] == 0:
            cyc = dfs(n)
            if cyc:
                return cyc
    return None


def req_defs(path):
    defs = {}
    if not os.path.isfile(path):
        return defs
    for _, line in read_unfenced(path):
        m = REQ_DEF.match(line)
        if m:
            defs[clean_cell(m.group(1))] = m.group(2)
    return defs


def main():
    if len(sys.argv) < 2:
        print(__doc__.strip())
        return 2
    base = sys.argv[1]
    path = os.path.join(base, '02-architecture.md')
    spec = os.path.join(base, '01-requirements.md')
    errors, warns = [], []

    if not os.path.isfile(path):
        errors.append('找不到 02-architecture.md')
        return report('check_architecture ' + base, errors, warns)

    pairs = read_unfenced(path)
    heads = sections(pairs)
    reqs = req_defs(spec)

    for name in ('简介', '资源', '沟通计划', '软件架构设计',
                 '模块清单', '模块契约', '追溯分析', '交接给详细设计'):
        if find_section(heads, name) is None:
            errors.append('缺少必需章节：' + name)
    for name in ('架构摘要', '外部接口', '数据定义', '动态行为', '软件环境', '资源消耗目标',
                 '软件调度机制', '异常清单', '假设和约束', '依赖矩阵'):
        if find_section(heads, name) is None:
            warns.append('建议补上章节：' + name)

    list_sec = find_section(heads, '模块清单')
    modules, deps = {}, {}
    if list_sec is not None:
        rows = table_rows(list_sec['body'])
        if not rows:
            errors.append('「模块清单」没有表格')
        else:
            header = rows[0][1]
            idx_module = col_index(header, '模块')
            idx_duty = col_index(header, '职责')
            idx_deps = col_index(header, '依赖')
            idx_layer = col_index(header, '层')
            if idx_module is None:
                errors.append('「模块清单」表头缺少「模块」列')
            if idx_duty is None:
                errors.append('「模块清单」表头缺少「职责」列')
            if idx_deps is None:
                warns.append('「模块清单」表头建议补「依赖（调用方向）」列')
            if idx_layer is None:
                warns.append('「模块清单」表头建议补「层」列')
            if idx_module is not None:
                for lineno, cells in rows[1:]:
                    if len(cells) <= idx_module:
                        continue
                    name = clean_cell(cells[idx_module])
                    if not name:
                        continue
                    if is_placeholder(name):
                        warns.append('第 %d 行模块名仍是占位符：%s' % (lineno, name))
                        continue
                    if name in modules:
                        errors.append('模块名重复：%s' % name)
                    modules[name] = lineno
                    if norm(name).lower() in ROLE_HINTS:
                        warns.append('第 %d 行模块名疑似分层类别或泛指角色，请确认它是具体模块：%s' % (lineno, name))
                    if idx_duty is not None and len(cells) > idx_duty and not clean_cell(cells[idx_duty]):
                        errors.append('模块 %s 缺少职责' % name)
                    deps[name] = []
                    if idx_deps is not None and len(cells) > idx_deps:
                        for dep in parse_deps(cells[idx_deps]):
                            if is_placeholder(dep):
                                warns.append('模块 %s 的依赖仍是占位符：%s' % (name, dep))
                                continue
                            deps[name].append(dep)
                if not modules:
                    errors.append('「模块清单」没有有效模块行')
                for name, dep_list in deps.items():
                    for dep in dep_list:
                        if dep not in modules:
                            warns.append('模块 %s 依赖的 %s 不在模块清单中' % (name, dep))
                cycle = find_cycle(deps)
                if cycle:
                    errors.append('模块依赖成环：' + ' → '.join(cycle))

    contract_sec = find_section(heads, '模块契约')
    covered = 0
    if contract_sec is not None:
        start = heads.index(contract_sec)
        seen = []
        for h in heads[start + 1:]:
            if h['level'] <= 2:
                break
            if h['level'] == 3:
                # 层标题：应用层 / 中间层 / 驱动层
                continue
            if h['level'] != 4:
                continue
            name = clean_cell(lint_common.strip_number(h['title']))
            seen.append(name)
            if re.search(r'↔|→|->', name):
                errors.append('第 %d 行模块节按调用对命名（%s）；请改成单个模块名' % (h['line'], h['title']))
                continue
            if is_placeholder(name):
                warns.append('第 %d 行模块契约名仍是占位符：%s' % (h['line'], name))
                continue
            if name not in modules:
                errors.append('第 %d 行模块契约引用了不存在的模块：%s' % (h['line'], name))
            body_text = '\n'.join(t for _, t in h['body'])
            m = re.search(r'\*\*覆盖 REQ\*\*\s*[：:]\s*(.+)', body_text)
            if not m:
                errors.append('%s 缺少「覆盖 REQ」：应列出本模块兑现的 REQ' % name)
            else:
                rids = REQ_IN_TEXT.findall(m.group(1))
                if not rids:
                    errors.append('%s 的「覆盖 REQ」没有 REQ 编号' % name)
                else:
                    covered += 1
                    for rid in rids:
                        if rid not in reqs:
                            errors.append('%s 覆盖了不存在的 %s' % (name, rid))
            if not any(k in body_text for k in ('公开接口', '事件与回调', '对外数据', '资源与约束', '无公开接口')):
                warns.append('第 %d 行 %s 的契约小节没有「公开接口 / 事件与回调 / 对外数据 / 资源与约束」内容' % (h['line'], name))
            rows = table_rows(h['body'])
            if rows:
                header = rows[0][1]
                if any('接口' in c for c in header) and not any('约束' in c for c in header):
                    warns.append('%s 的公开接口表建议加「约束」列（格式 / 大小 / 频率）' % name)
        dup = set()
        for name in seen:
            if name in dup:
                errors.append('模块契约节重复：%s' % name)
            dup.add(name)
        for name in sorted(set(modules) - set(seen)):
            errors.append('模块清单里的 %s 没有「模块契约」小节' % name)
    else:
        errors.append('缺少「模块契约」节，无法核对覆盖')

    # 追溯分析：每条被覆盖的 REQ 至少出现在追溯表里
    trace = find_section(heads, '追溯分析')
    if trace is not None and covered:
        ttext = section_text(heads, trace)
        for rid in sorted(set(reqs)):
            if rid not in ttext:
                warns.append('追溯分析里没有 %s（建议在「软件需求 → 架构元素」表补一行）' % rid)

    raw = open(path, encoding='utf-8').read()
    for ln, msg in lint_common.placeholder_issues(raw):
        errors.append('第 %d 行：%s' % (ln, msg))
    if not lint_common.has_role_header(raw, '架构师'):
        errors.append('缺少文档头：> 角色：架构师 ｜ 依据：…')
    warns.extend(lint_common.heading_order_warnings(
        raw, ['简介', '资源', '沟通计划', '软件架构设计',
              '模块契约', '追溯分析', '交接给详细设计']))

    print('模块：%d ｜ 覆盖 REQ 的模块：%d' % (len(modules), covered))
    return report('check_architecture ' + base, errors, warns)


if __name__ == '__main__':
    sys.exit(main())

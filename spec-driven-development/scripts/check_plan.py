#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""方案结构检查（02-plan.md / 02-plan-contracts.md）。

只查机械事实：模块划分节、模块清单、依赖方向、契约引用和依赖环。
层名/角色名只做提示，不判语义；模块粒度好不好由门 2 判断。

用法: python check_plan.py <项目>/SDD
"""

import os
import re
import sys
import lint_common

FENCE = re.compile(r'^\s*(?:' + (chr(96) * 3) + r'|~~~)')
# 仅用于提示，不参与错误判定；模块语义由门 2 判断。
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


def is_role_hint(s):
    return norm(clean_cell(s)).lower() in ROLE_HINTS


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
        return None

    for n in graph:
        if color[n] == 0:
            cyc = dfs(n)
            if cyc:
                return cyc
    return None


def main():
    if len(sys.argv) < 2:
        print(__doc__.strip())
        return 2
    base = sys.argv[1]
    plan_path = os.path.join(base, '02-plan.md')
    contracts_path = os.path.join(base, '02-plan-contracts.md')
    errors, warns = [], []

    if not os.path.isfile(plan_path):
        errors.append('找不到 02-plan.md')
        return report('check_plan ' + base, errors, warns)

    if not os.path.isfile(contracts_path):
        warns.append('没有 02-plan-contracts.md；如果本次没有内部契约，请在 02-plan.md 写明「无内部契约」')

    plan_pairs = read_unfenced(plan_path)
    plan_heads = sections(plan_pairs)
    for section_name in ('方案总览', '需求可行性', '质量属性', '关键决策', '风险与应对', '交付', '验证手段', '交接给任务拆解'):
        if find_section(plan_heads, section_name) is None:
            warns.append('02-plan.md 建议补上「%s」节（技术总监视角）' % section_name)
    module_sec = find_section(plan_heads, '模块划分')
    modules = {}
    deps = {}

    if module_sec is None:
        errors.append('02-plan.md 缺少「模块划分」节')
    else:
        rows = table_rows(module_sec['body'])
        if not rows:
            errors.append('「模块划分」节里没有表格')
        else:
            header = rows[0][1]
            idx_module = col_index(header, '模块')
            idx_duty = col_index(header, '职责')
            idx_tables = col_index(header, '拥有', '表')
            idx_deps = col_index(header, '依赖')
            idx_write = col_index(header, '写权限')
            idx_layer = col_index(header, '层')
            if idx_layer is None:
                idx_layer = col_index(header, '分类')
            required = [
                ('层 / 分类', idx_layer),
                ('模块', idx_module), ('职责', idx_duty),
                ('拥有或读写的表', idx_tables), ('依赖', idx_deps),
                ('写权限', idx_write),
            ]
            for label, idx in required:
                if idx is None:
                    errors.append('「模块划分」表头缺少列：' + label)
            if all(idx is not None for _, idx in required):
                for lineno, cells in rows[1:]:
                    if len(cells) <= max(idx_module, idx_duty, idx_tables, idx_deps, idx_write):
                        errors.append('第 %d 行模块表列数不足' % lineno)
                        continue
                    name = clean_cell(cells[idx_module])
                    if not name:
                        errors.append('第 %d 行模块名为空' % lineno)
                        continue
                    if is_placeholder(name):
                        warns.append('第 %d 行模块名仍是占位符：%s' % (lineno, name))
                    if name in modules:
                        errors.append('模块名重复：%s' % name)
                    modules[name] = (lineno, cells)
                    if is_role_hint(name):
                        warns.append('第 %d 行模块名疑似分层类别或泛指角色，请确认它是具体模块：%s' % (lineno, name))
                    if not clean_cell(cells[idx_duty]):
                        errors.append('模块 %s 缺少职责' % name)
                    if not clean_cell(cells[idx_tables]):
                        errors.append('模块 %s 缺少「拥有或读写的表」' % name)
                    if not clean_cell(cells[idx_write]):
                        errors.append('模块 %s 缺少写权限' % name)
                    elif is_placeholder(clean_cell(cells[idx_write])):
                        warns.append('模块 %s 的写权限仍是占位符' % name)
                if not modules:
                    errors.append('「模块划分」没有有效模块行')

                for name, (lineno, cells) in modules.items():
                    deps[name] = []
                    for dep in parse_deps(cells[idx_deps]):
                        if is_placeholder(dep):
                            warns.append('模块 %s 的依赖仍是占位符：%s' % (name, dep))
                            continue
                        deps[name].append(dep)
                        if dep not in modules:
                            warns.append('模块 %s 依赖的 %s 不在模块清单中' % (name, dep))

    cycle = find_cycle(deps) if deps else None
    if cycle:
        errors.append('模块依赖成环：' + ' → '.join(cycle))

    gate = find_section(plan_heads, '门 2')
    if gate is None:
        warns.append('02-plan.md 缺少「门 2」节')
    else:
        gate_text = '\n'.join(t for _, t in gate['body'])
        if '模块划分' not in gate_text:
            warns.append('门 2 清单没有提到模块划分')
        concl = [t for _, t in gate['body'] if '结论' in t]
        if not concl:
            errors.append('门 2 小节里没有结论行')
        else:
            text = ' '.join(concl)
            if re.search(r'<[^>]*>', text):
                errors.append('门 2 结论仍是占位符：' + text.strip()[:60])
            elif 'reject' in text.lower():
                errors.append('门 2 结论是 reject，必须退回上游修完重跑')
            elif 'approve' in text.lower() and '裁决人' in text and '日期' in text:
                pass
            elif '待审' in text or '未审' in text:
                warns.append('门 2 结论仍是待审（尚未获得批准）')
            else:
                errors.append('门 2 结论格式不明，应为 approve ｜ 裁决人：… ｜ 日期：… 或 待审')

    contracts_exists = os.path.isfile(contracts_path)
    contracts_heads = []
    if contracts_exists:
        contracts_pairs = read_unfenced(contracts_path)
        contracts_heads = sections(contracts_pairs)
        for name in ('模块清单', '依赖方向', '模块间契约'):
            if find_section(contracts_heads, name) is None:
                errors.append('02-plan-contracts.md 缺少「%s」节' % name)

    contract_modules = set()
    list_sec = find_section(contracts_heads, '模块清单')
    if list_sec is not None:
        rows = table_rows(list_sec['body'])
        if not rows:
            errors.append('「模块清单」没有表格')
        else:
            header = rows[0][1]
            idx_module = col_index(header, '模块')
            if idx_module is None:
                errors.append('「模块清单」表头缺少「模块」列')
            else:
                for lineno, cells in rows[1:]:
                    if len(cells) <= idx_module:
                        continue
                    name = clean_cell(cells[idx_module])
                    if not name:
                        continue
                    contract_modules.add(name)
                    if is_placeholder(name):
                        warns.append('第 %d 行契约模块名仍是占位符：%s' % (lineno, name))
                    if is_role_hint(name):
                        warns.append('第 %d 行契约模块名疑似分层类别或泛指角色，请确认它是具体模块：%s' % (lineno, name))
                    if name not in modules:
                        errors.append('契约模块清单里的 %s 不在 02-plan.md 的「模块划分」中' % name)
                if not contract_modules:
                    errors.append('「模块清单」没有有效模块行')

    contract_sec = find_section(contracts_heads, '模块间契约')
    contracts = []
    if contract_sec is not None:
        start = contracts_heads.index(contract_sec)
        for h in contracts_heads[start + 1:]:
            if h['level'] <= 2:
                break
            if h['level'] == 3:
                m = re.match(r'^(.+?)\s*(?:↔|→|->)\s*(.+)$', h['title'])
                if m:
                    a = clean_cell(m.group(1))
                    b = clean_cell(m.group(2))
                    contracts.append((h['line'], a, b))
                    for name in (a, b):
                        if is_placeholder(name):
                            warns.append('第 %d 行契约模块名仍是占位符：%s' % (h['line'], name))
                        else:
                            if is_role_hint(name):
                                warns.append('第 %d 行契约模块名疑似分层类别或泛指角色，请确认它是具体模块：%s' % (h['line'], name))
                            if name not in modules:
                                errors.append('第 %d 行契约引用了不存在的模块：%s' % (h['line'], name))
                            if name not in contract_modules:
                                errors.append('第 %d 行契约引用的 %s 不在「模块清单」中' % (h['line'], name))
                    if a == b:
                        errors.append('第 %d 行契约两端是同一个模块：%s' % (h['line'], a))
                else:
                    warns.append('第 %d 行契约标题无法解析模块对：%s' % (h['line'], h['title']))
        if not contracts and '无内部契约' not in '\n'.join(t for _, t in contract_sec['body']):
            warns.append('「模块间契约」没有找到 A → B / A ↔ B 形式的契约')

    print('模块：%d ｜ 契约：%d' % (len(modules), len(contracts)))
    raw = open(plan_path, encoding='utf-8').read()
    for ln, msg in lint_common.placeholder_issues(raw):
        errors.append('第 %d 行：%s' % (ln, msg))
    if not lint_common.has_role_header(raw, '技术总监'):
        errors.append('缺少文档头：> 角色：技术总监 ｜ 依据：…')
    warns.extend(lint_common.heading_order_warnings(raw, ['方案总览', '需求可行性核对', '技术上下文', '模块划分', '数据与契约', '质量属性与约束', '关键决策与备选', '风险与应对', '交付', '验证手段', '宪法检查', '门 2', '交接给任务拆解', '修订记录']))
    return report('check_plan ' + base, errors, warns)


if __name__ == '__main__':
    sys.exit(main())

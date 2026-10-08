# 示例：为 CLI 工具新增 --json 输出

## 变更请求

"给 converter.py 加一个 --json 参数，输出 JSON 格式的结果。"

## 第 1 步：建立规格

创建 `specs/add-json-output/spec.md`：

```markdown
# 变更规格：add-json-output

## 背景
converter.py 目前只输出人类可读文本，下游脚本无法稳定解析结果。

## 目标
支持 `--json` 参数，以机器可读的 JSON 输出转换结果。

## 范围
仅修改 `converter.py` 的参数解析与输出逻辑；不改动转换核心算法。

## 非目标
不支持 YAML 输出；不改变默认（无参数时）的文本输出格式。

## 影响面
`README.md` 的用法说明需要补充；`tests/` 需新增 JSON 输出用例。

## 验收标准
- `python converter.py input.txt --json` 输出合法 JSON
- 不带 `--json` 时输出与改动前完全一致
- `README.md` 包含 `--json` 的用法说明
```

## 第 2 步：规格门禁

```bash
python scripts/check_spec.py specs/add-json-output/spec.md
# 输出：规格校验通过
```

## 第 3 步：用户确认

向用户呈现规格摘要，收到"确认"后进入拆解；未确认前不修改任何代码。

## 第 4 步：任务拆解

`specs/add-json-output/tasks.md`：

```markdown
# 任务清单：add-json-output

- [ ] 1. 在 converter.py 增加 --json 参数解析
      验证：`python converter.py input.txt --json` 输出 JSON
- [ ] 2. 保持默认文本输出不变
      验证：对比改动前后的无参数输出一致
- [ ] 3. 补充 README 用法说明
      验证：README 包含 --json 示例
```

## 第 5 步：逐任务实施与验收

按清单顺序实施，每完成一项勾选并执行验证命令；全部完成后对照验收标准逐条核对，最后更新 README 与 CHANGELOG。
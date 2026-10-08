# 02-plan-contracts（Phase 1）

> **按需生成**——变更不涉及模块间接口时，本文件不必存在。
> **职责**：模块间的软件接口——函数签名、协议帧格式、错误码，**按执行上下文分层**。
> **消费者**：各模块实现；`analyze` 检查它与 spec / plan 是否自洽。

> **按执行上下文分层标注**——`@context: isr` 与 `@context: task` 分开写。
> 混排的代价：ISR 里误调不会编译报错，只会在最坏情况暴露。

## @context: isr

### `can_dispatch()`

| 项 | 说明 |
|---|---|
| 签名 | `void can_dispatch(const can_frame_t *f)` |
| 前置 | 仅中断上下文调用 |
| 禁止 | 不得调用任何 Flash 擦写 / 阻塞 API |

## @context: task

### `download_action()`

<…>


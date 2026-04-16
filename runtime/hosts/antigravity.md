# AntiGravity Adapter Notes

`AntiGravity` 在 `My-Way v0` 里按“自动激活优先、低噪声优先”的宿主来处理。
默认先做稳定伴随，不追求一开始就做重型 hook 编排。

## 1. 目标

- 保持 `always-on companion` 的自然感
- 让 `My-Way` 的存在不显著增加交互负担
- 只在必要时留下可恢复上下文的短笔记

## 2. 最小接入合同

### Prompt-only

- 宿主识别到相关任务后，默认启用 `My-Way`
- 回合开始时做最小 `Prelude`
- 回合结束后写最小 `Postlude`

### Hook-enhanced

只有在本地确认存在稳定开始/结束或执行反馈信号时，才提升：

- 开始信号 -> `turn_start / prelude`
- 执行反馈 -> `execute`
- 结束信号 -> `postlude`

## 3. 低噪声规则

- 能 `bypass` 时不强行改写
- 能一句记清时不写成长笔记
- 能转交 owner 时不继续扩写 companion 内容

## 4. 禁止事项

- 不把宿主自动激活语义误当成治理权限
- 不把 `My-Way` 变成额外的任务管理器
- 不在没有材料的情况下触发 reflection 融合

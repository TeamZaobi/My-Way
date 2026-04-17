# Claude Code Adapter Notes

`Claude Code` 是 `My-Way v0` 的优先宿主适配目标。
在这个骨架里，默认把它当作最适合首先推进到 `Hook-enhanced` 的宿主。

## 1. 目标

- 用更稳定的宿主信号把 `Prelude / Execute / Postlude` 分开
- 仍然维持 companion 定位，不把 `My-Way` 扩成 runtime owner
- 让 reflection triage 只在材料充分时触发

## 2. 推荐映射

如果宿主提供足够细的事件面，优先按下面的逻辑接入：

- 用户提交本轮请求 -> `turn_start / prelude`
- 工具调用前后或中间执行观察点 -> `execute`
- 当前回合停止或子任务结束 -> `postlude`
- 只有出现稳定模式或 reflection 相关材料 -> `fusion_review`

这只是适配层建议，不改变核心协议。

## 3. Companion 约束

- `Prelude` 仍然只能输出 `rewrite-light / bypass / observe-only`
- `Postlude` 仍然一轮最多一条短笔记
- 治理与同步执行仍然交给 `governance-authority` / `lifecycle-authority`

## 4. Fallback

- 即使可用信号更多，也先做记录和摘要，再考虑 guardrail
- 某类事件不稳定时，回退到更粗粒度的 `Prompt-only`
- 无法确认材料价值时，不触发 reflection triage

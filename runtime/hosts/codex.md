# Codex Adapter Notes

`Codex` 在 `My-Way v0` 里默认按 `Prompt-only` 设计。
只有当宿主明确提供可验证的开始、返回或结束信号时，才提升到 `Hook-enhanced`。

## 1. 目标

- 让 `My-Way` 在 Codex 中始终以轻量 companion 方式工作
- 不把宿主实验性能力误当成完整治理边界
- 优先跑通 `Prelude + Postlude`，再考虑更细粒度挂接

## 2. 最小接入合同

### Prompt-only

- 新 turn 到来时做一次 `Prelude`
- assistant 完成这一轮后补一条 `Postlude`
- 若问题落到治理或 skill 生命周期，直接转交 owner

### Hook-enhanced

只有在本地验证可用后，才接以下观察点：

- turn 开始信号
- 工具或命令返回信号
- turn 结束信号

映射原则：

- 开始信号 -> `turn_start / prelude`
- 返回信号 -> `execute`
- 结束信号 -> `postlude`

## 3. Fallback

- 没有稳定 hook 时，不伪造事件流
- 看不到工具返回细节时，只保留结果摘要
- 不能确定 source 或 owner 时，保持 `My-Way` 伴随角色

# Codex Adapter Notes

`Codex` 在 `My-Way v0` 里默认按 `Prompt-only` 设计。
只有当宿主明确提供可验证的开始、返回或结束信号时，才提升到 `Hook-enhanced`。

## 1. 目标

- 让 `My-Way` 在 Codex 中始终以轻量 companion 方式工作
- 不把宿主实验性能力误当成完整治理边界
- 优先跑通 `Prelude + Postlude`，再考虑更细粒度挂接

## 2. 最小接入合同

### Prompt-only

- 新 turn 到来时，先做一次最小 `carry-forward recall`
- 然后做一次 `Prelude`，同时决定这轮是否需要额外的 `method hooks` 和 `capability mounts`
- assistant 完成这一轮后补一条 `Postlude`
- 如果这轮出现可复用的稳定上下文，再派生一个可选 `carry-forward candidate`
- promoted candidate 再合并进 durable carry-forward store
- 若问题落到治理或 skill 生命周期，直接转交 owner

### Hook-enhanced

只有在本地验证可用后，才接以下观察点：

- turn 开始信号
- 工具或命令返回信号
- turn 结束信号

映射原则：

 - 开始信号 -> `turn_start / carry-forward recall / prelude(intent translation / method select / capability mount)`
 - 返回信号 -> `execute`
 - 结束信号 -> `postlude -> carry-forward candidate -> durable carry-forward store`

推荐命令面：

```bash
python scripts/myway_runtime.py finalize-turn \
  --input-json /path/to/postlude.note.json \
  --note-path /path/to/turn.note.json \
  --history-path /path/to/turn.notes.history.jsonl \
  --candidate-path /path/to/turn.carryforward.candidate.json \
  --carryforward-log-path /path/to/turn.carryforward.log.jsonl \
  --carryforward-store-path /path/to/turn.carryforward.store.jsonl
```

约束：

- hook 只需要构造一份 `turn.note` 结构的 JSON
- `My-Way` 自己负责 note 落盘、carry-forward sidecar 判断、durable store consolidation 和 recall plan
- 这个 sidecar 是可选耐久上下文，不是隐藏用户记忆

## 3. Fallback

- 没有稳定 hook 时，不伪造事件流
- 看不到工具返回细节时，只保留结果摘要
- 不能确定 source 或 owner 时，保持 `My-Way` 伴随角色

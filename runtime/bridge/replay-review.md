# Reflection Bridge Replay / Review

这份协议回答一个问题：如何从固定 artifact 里重放一次 triage 判断。

## 1. 回放输入

回放时最少要拿到：

1. `turn.events.jsonl`
2. `turn.note.json`
3. `reflection.exchange.packet.json`
4. `reflection-triage-audit.jsonl` 中对应那一条记录

## 2. 回放步骤

1. 先定位 `audit record` 的 `packet_id` 和 `turn_id`
2. 从 `turn.events.jsonl` 切出同一 `turn_id` 的事件序列
3. 读取同一 `turn_id` 的 `turn.note.json`
4. 读取 `reflection.exchange.packet.json`
5. 对照 `evidence_refs` 和 `replay_refs`
6. 重新判断：
   - 材料是否充分
   - `decision` 是否还能成立
   - `follow_up_owner` 是否越权

## 3. 复核结论

复核只允许四种结论：

- `confirmed`
- `needs-more-evidence`
- `routing-adjustment`
- `reject`

## 4. Stop rules

下面情况不允许继续推进：

- `evidence_refs` 为空或无法定位
- `replay_refs` 缺失
- `packet_id` 与审计记录不一致
- 高影响候选没有停在 review gate

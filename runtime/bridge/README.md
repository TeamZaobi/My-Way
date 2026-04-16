# My-Way Reflection Bridge Contract

`bridge/` 只处理一件事：把外部反思来源与 `My-Way` 的融合判断落成可回放、可审计的 triage 记录。
它不是新的 router，也不是自动同步执行层。

## 1. 输入

最小输入固定为四类：

1. `turn.events.jsonl`
   - 本轮事实切片
2. `turn.note.json`
   - 本轮短笔记
3. `reflection.exchange.packet.json`
   - 交换材料
4. `reflection-triage-audit.jsonl`
   - 追加式 triage 审计

## 2. 触发条件

只有下面情况才跑 triage：

- 本轮明确产出了 reflection 交换包
- 交换包里有非空 `evidence`
- 这轮确实值得输出 `adopt / diverge / upstream-candidate`

下面情况必须降级为 `bypass`：

- replay 依据缺失，无法回放本轮判断
- 材料不足，只剩一句空泛 summary
- 同一 `packet_id` 已经被审计过，且没有新证据

## 3. 输出

triage 只输出一条 audit record，最小字段包括：

- `turn_id`
- `packet_id`
- `decision`
- `reason`
- `follow_up_owner`
- `evidence_refs`
- `replay_refs`

## 4. Owner 约束

- `decision = adopt | diverge`
  - 默认仍由 `my-way` 收束
- `decision = upstream-candidate`
  - 只形成候选，不自动 mutation
- 涉及治理边界
  - 转 `governance-owner`
- 涉及 live asset、同步执行、分发
  - 转 `lifecycle-owner`

## 5. 去重与回放

- 先按 `packet_id` 去重
- 再依赖 `turn_id + replay_refs` 重建判断链
- replay 无法重现时，记录保留，但不得推进到更高层级

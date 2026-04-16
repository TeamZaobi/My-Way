# My-Way System Architecture v0.1

## 1. 架构目标

`My-Way` 要成为一个跨宿主、始终触发的 companion meta-skill，但不膨胀成新的 agent runtime。

架构目标只有五个：

1. 跨宿主保持同一套 turn 语义
2. 每轮稳定执行 `Prelude + Postlude`
3. 事件和笔记分层，不混长期记忆
4. 与外部反思来源做可审计的三态融合判断
5. 在任何混合问题上维持单写口

## 2. 架构总览

```text
Host signals
  -> Host adapter
  -> My-Way core state machine
  -> Event layer
  -> Notes layer
  -> Reflection bridge
  -> Routing / handoff
```

## 3. 分层说明

### 3.1 Host adapter

负责把不同宿主的生命周期信号转换成统一 turn event。

职责：

- 识别用户输入开始
- 识别宿主执行中间结果
- 识别回合结束
- 标注宿主来源和能力级别

不负责：

- 记忆判断
- 反思融合
- 项目治理
- skill 生命周期同步

### 3.2 My-Way core

`My-Way core` 只负责一条确定性的 turn state machine：

`idle -> prelude -> execute -> postlude -> fusion-review -> idle`

职责：

- 生成轻量 `Prelude`
- 决定 `rewrite-light / bypass / observe-only`
- 生成短 `Postlude`
- 判断本轮是否值得进入融合复盘

### 3.3 Event layer

事件层保存最小事实，要求 append-only。

作用：

- 保存发生过什么
- 供回合笔记和融合判断回看
- 避免 observation 与 curated note 混层

### 3.4 Notes layer

只保存人能读的简短回合笔记。

作用：

- 帮助下一轮恢复上下文
- 给人提供可读总结
- 控制噪声，不做无限增长的全量日志

### 3.5 Reflection bridge

只交换“可思考的融合材料”。

职责：

- 接收外部反思来源导出的变化材料
- 接收 `My-Way` 本地产出的稳定候选
- 输出 `adopt / diverge / upstream-candidate`

不负责：

- 直接修改外部系统
- 直接修改公共 skill

### 3.6 Routing / handoff

保持单写口。

- 治理问题 -> `governance-owner`
- 生命周期 / 同步执行问题 -> `lifecycle-owner`
- `My-Way` 只负责伴随、笔记、融合判断

## 4. 宿主模式

### 4.1 Prompt-only

- 无 hook
- best-effort 模式
- 只保证轻量前后处理

### 4.2 Hook-enhanced

- 宿主能提供开始、执行、结束等信号
- `Prelude + Postlude` 更稳定

### 4.3 Fusion-enabled

- 在 `Hook-enhanced` 之上，具备外部反思交换材料输入
- 才进入正式融合回路

## 5. Turn state machine

### 5.1 状态

- `idle`
- `prelude`
- `execute`
- `postlude`
- `fusion-review`

### 5.2 转移

- `idle -> prelude`
  - 接收到新 turn
- `prelude -> execute`
  - 生成 `rewrite-light / bypass / observe-only`
- `execute -> postlude`
  - 宿主或 IDE 返回本轮结果
- `postlude -> fusion-review`
  - 本轮出现值得沉淀或对照外部反思来源的材料
- `fusion-review -> idle`
  - 记录 triage 结果后结束

## 6. Turn event schema

```yaml
turn_event:
  event_id: string
  turn_id: string
  timestamp: iso-8601
  host_id: codex | claude-code | antigravity | other
  mode: prompt-only | hook-enhanced | fusion-enabled
  phase: turn_start | prelude | execute | postlude | fusion_review | handoff
  source: user | host | my-way | reference-system
  payload_summary: string
  related_paths?: [string]
  confidence?: low | medium | high
  source_tag?: string
  event_hash?: string
```

规则：

- append-only
- 允许最小 payload summary，不强求全量原始内容
- `event_hash` 用于去重

## 7. Note schema

```yaml
turn_note:
  note_id: string
  turn_id: string
  scope: session | project | global-candidate
  goal: string
  actions: string
  result: string
  candidate_points?: [string]
  retention: short | medium | review-required
```

规则：

- 每轮最多一条短笔记
- 默认先落 `session`
- 只有重复出现或明确重要时才提升到 `project`
- 不直接写 `global`

## 8. Reflection exchange packet

```yaml
reflection_exchange_packet:
  packet_id: string
  source_system: reference-system | my-way
  target_system: my-way | reference-system
  material_type: note | pattern | workflow | guardrail | memory | skill_candidate
  layer: worldview | workflow | guardrail | implementation
  summary: string
  evidence: [string]
  candidate_action: adopt | diverge | upstream-candidate
  local_decision_reason?: string
  follow_up_owner?: my-way | governance-owner | lifecycle-owner
```

## 9. 所有权与转交

| 问题类型 | Primary owner | My-Way 动作 |
|---|---|---|
| 回合前置整理、回合后笔记 | `my-way` | 主责 |
| 项目真源、写权、治理边界 | `governance-owner` | 观察、转交、补笔记 |
| skill live asset、同步执行、投影、分发 | `lifecycle-owner` | 观察、转交、补笔记 |
| 外部反思内容 triage | `my-way` | 主责 |
| triage 后需资产同步 | `lifecycle-owner` | 接收提案 |
| triage 后影响治理边界 | `governance-owner` | 接收提案 |

## 10. 护栏

### 10.1 Intent drift

- `Prelude` 只允许轻量整理
- 允许 `bypass / observe-only`

### 10.2 Recursion

- 用 `turn_id`
- 用 `source_tag`
- 用 `cooldown`
- 用 `event_hash`

### 10.3 Noise control

- 每轮一条短笔记
- 不做全局长日志
- observation 与 note 分层

### 10.4 Mutation control

- `v0` 只做 triage
- 高影响动作默认 review gate

## 11. 演进路线

### v0

- turn state machine
- turn event schema
- short note schema
- reflection exchange packet
- owner routing

### v1

- 分层记忆
- retrieval-before-action
- confidence / pruning / self-validation

### v2

- 外部验证面
- 离线实验分支

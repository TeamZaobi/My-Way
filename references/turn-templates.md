# My-Way Turn Templates

这个文件只固定 `My-Way v0` 的最小输出协议。
模板服务于宿主集成和文档实现，不代表每轮都必须把这些字段完整展示给最终用户。

## 1. Prelude template

只在需要前置整理时生成，输出保持短小。

```yaml
prelude:
  mode: rewrite-light | bypass | observe-only
  user_goal: string
  action_focus: string
  method_hooks:
    - string
  capability_mounts:
    - string
  hard_constraints:
    - string
  owner: my-way | host | governance-owner | lifecycle-owner
```

字段规则：

- `mode`
  - 三选一，不允许混合状态
- `user_goal`
  - 只复述用户真正要解决的问题，不扩写新任务
- `action_focus`
  - 当前最适合执行的动作
- `method_hooks`
  - 最多 3 条；只写这一轮真正要挂上的验收 / 审核 / 解题方法钩子
- `capability_mounts`
  - 最多 3 条；只写这一轮真正需要默认挂载的底层能力面
- `hard_constraints`
  - 最多 3 条；只保留不能丢的边界
- `owner`
  - 明确这一轮谁主导

## 2. Handoff note template

只在判断需要转交时生成。

```yaml
handoff_note:
  target: governance-owner | lifecycle-owner
  reason: string
  my_way_role: observe | context-pack | note
  carry_over:
    - string
```

字段规则：

- `target`
  - 只允许单 owner
- `reason`
  - 说清为什么这不是 `My-Way` 主责
- `my_way_role`
  - `My-Way` 只保留伴随角色
- `carry_over`
  - 只写必要上下文，不做重复摘要

## 3. Postlude template

每轮最多一条短笔记，默认作用域是 `session`。

```yaml
postlude:
  scope: session | project | global-candidate
  goal: string
  actions: string
  result: string
  candidate_points:
    - string
```

字段规则：

- `scope`
  - 默认 `session`
- `goal`
  - 这轮原始目标
- `actions`
  - 实际发生了什么
- `result`
  - 当前阶段性结果
- `candidate_points`
  - 没有就留空；有也不超过 3 条

提升规则：

- 只有重复出现的稳定模式，才从 `session` 提升到 `project`
- 只有跨项目、跨宿主或外部反思相关材料，才允许进入 `global-candidate`

## 4. Carry-forward candidate template

只在 `Postlude` 之后运行，用来判断这轮内容是否值得形成耐久 sidecar。

```yaml
carryforward_candidate:
  decision: skip | carry-forward
  candidate_type: none | preference | constraint | method-pattern | capability-mount-rule | workflow-pattern | routing-rule | external-pattern | project-context
  candidate_text: string
  rationale: string
  evidence:
    - string
```

字段规则：

- `decision`
  - `skip` 表示只保留 note，不派生 sidecar
  - `carry-forward` 表示这轮出现了值得复用的耐久上下文
- `candidate_type`
  - `preference`
    - 稳定偏好，例如默认写法、默认协作方式、固定不做什么
  - `constraint`
    - 长期约束、不可越过的 guardrail
  - `method-pattern`
    - 能迁移到后续回合的验收 rubric、审核方法、解题 playbook 或思维模型
  - `capability-mount-rule`
    - 进入同类任务时应默认挂载的通用能力挂件或能力面
  - `workflow-pattern`
    - 能重复使用的流程、cutover、接缝或整理模式
  - `routing-rule`
    - 能稳定减少漂移的 authority / handoff 规则
  - `external-pattern`
    - 外部成熟项目的可复用经验
  - `project-context`
    - 需要跨回合保留的长期项目上下文
- `candidate_text`
  - 用一句话写清以后仍值得带上的上下文
- `rationale`
  - 解释为什么它值得形成耐久 sidecar，或为什么本轮应跳过
- `evidence`
  - 最多 3 条，直接来自 note 或本轮稳定结论

吸收规则：

- 出现明确偏好、长期约束、成熟方法模式、通用 capability mount 规则、authority 边界、外部成熟项目经验时，可直接进入 `carry-forward`
- `workflow-pattern` 与 `project-context` 至少要有重复信号或更高 retention，才值得提升
- 一次性修补、临时计划、原始日志和未证实猜测一律跳过

## 5. Durable carry-forward record template

promoted candidate 通过后，要先合并成 durable record，不能直接把 candidate 当成长期上下文总表。

```yaml
carryforward_record:
  record_id: string
  record_key: string
  candidate_type: preference | constraint | method-pattern | capability-mount-rule | workflow-pattern | routing-rule | external-pattern | project-context
  candidate_text: string
  status: active | superseded | archived
  preferred_injection_slot: method-hooks | capability-mounts | hard-constraints | carry-over
  reinforcement_count: integer
  source_turn_ids:
    - string
```

规则：

- `record_key`
  - 长期 merge / upsert 的稳定键
- `preferred_injection_slot`
  - 说明 recall 时默认注入到哪一层
- `reinforcement_count`
  - 不是日志条数，而是被稳定复用的次数信号

## 6. Carry-forward recall plan template

新 turn 进入时，durable store 只输出一份 bounded recall plan。

```yaml
carryforward_recall:
  query_text: string
  selected_records:
    - record_id: string
      candidate_type: string
      injection_slot: method-hooks | capability-mounts | hard-constraints | carry-over
      reason: string
  recommended_method_hooks:
    - string
  recommended_capability_mounts:
    - string
  recommended_hard_constraints:
    - string
  carry_over_points:
    - string
```

规则：

- `selected_records`
  - 最多少量条目；只带回当前 turn 真正相关的 durable records
- `recommended_*`
  - recall 的目标是直接服务 `Prelude`，而不是回放长期上下文全文

## 7. Reflection triage template

只在满足融合触发条件时生成。

```yaml
reflection_triage:
  material_source: reference-system | my-way
  layer: worldview | workflow | guardrail | implementation
  summary: string
  decision: adopt | diverge | upstream-candidate
  rationale: string
  follow_up_owner: my-way | governance-owner | lifecycle-owner
```

字段规则：

- `material_source`
  - 说明材料来自哪边
- `layer`
  - 强制判断变化位于哪一层
- `summary`
  - 只保留融合判断必需的信息
- `decision`
  - `v0` 固定三态
- `rationale`
  - 说明为什么吸收、保留分歧或回送候选
- `follow_up_owner`
  - 只有涉及实际资产修改时才交给 `governance-owner` 或 `lifecycle-owner`

## 8. Stop rules

出现下面任一情况时，`My-Way` 应主动收住：

- 用户原话已经足够清楚，直接 `bypass`
- 本轮只是普通执行，无稳定新模式，不触发 reflection triage
- 需要治理或同步执行，但 owner 已明确，应转交而不是继续扩写 companion 内容
- 额外整理只会制造噪声或引入意图漂移

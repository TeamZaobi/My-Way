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

## 4. Reflection triage template

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

## 5. Stop rules

出现下面任一情况时，`My-Way` 应主动收住：

- 用户原话已经足够清楚，直接 `bypass`
- 本轮只是普通执行，无稳定新模式，不触发 reflection triage
- 需要治理或同步执行，但 owner 已明确，应转交而不是继续扩写 companion 内容
- 额外整理只会制造噪声或引入意图漂移

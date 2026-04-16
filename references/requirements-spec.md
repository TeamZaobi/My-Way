# My-Way Requirements Spec v0.1

## 1. 项目定位

`My-Way` 是一个始终触发的常驻 `companion meta-skill` 骨架，服务于 `Codex`、`Claude Code`、`AntiGravity` 等 AI-Native 开发工具宿主环境。
公开版只定义可移植的 companion 协议和最小运行面，不携带个人记忆、私有 owner 命名或内部系统约定。

## 2. 核心目标

- 在不同宿主环境中维持更连续、更一致的 companion 行为
- 每轮先做轻量前置整理，再在回合结束后补简短笔记
- 与外部反思来源保持持续的、非机械的、可审计的融合判断
- 在“外置化、多宿主、轻量常驻、可审计 triage”这条线上保持可复用

## 3. 核心能力

- `Always-on`
  - 默认每轮触发，不依赖用户显式点名
  - 工程上被定义为“宿主级集成契约”，不是单靠 skill 文本自动常驻
- `Prelude`
  - 把用户自然语言整理成更适合当前宿主和工具执行的表述
- `Postlude`
  - 在宿主或 IDE 完成这一轮返回后，自动补一条简短笔记
- `Lightweight observation`
  - 执行过程中做轻量记录和思考，但不抢主流程
- `Host-agnostic behavior`
  - 尽量保持跨宿主一致的行为，不把本体绑死在单一工具的私有机制上
- `Reflection triage`
  - 读取外部反思来源的材料，经过判断后融合
  - 把 `My-Way` 本地成熟模式整理成可回流的候选内容

## 4. 不可妥协约束

- `no silent intent drift`
  - 不得静默改写用户真实意图
- `bypass / no-op required`
  - 当用户请求已经足够清楚、宿主可直接执行、或额外整理只会制造漂移时，必须允许 `Prelude` 不改写
- `proposal before mutation`
  - 先形成判断和提案，再考虑高影响变更
- `single-owner routing`
  - 任一混合问题必须有一个主责 owner
- `compact notes by default`
  - 回合笔记默认短小，不直接升级成全局记忆
- `host-fallback`
  - 没有理想 hook 的宿主必须支持降级模式，而不是伪装成完全支持

## 5. 宿主集成模式

### 5.1 Prompt-only

- 没有显式 hook
- `My-Way` 只能 best-effort 地做轻量前后处理

### 5.2 Hook-enhanced

- 宿主可以提供回合开始、工具返回、回合结束等生命周期信号
- `My-Way` 能稳定执行 `Prelude + Postlude`

### 5.3 Fusion-enabled

- 在 `Hook-enhanced` 之上，具备外部反思交换材料输入
- `My-Way` 才进入正式融合判断

## 6. 每轮默认工作流

1. 用户发出请求
2. `My-Way` 先做轻量前置整理
3. 主任务交给当前宿主环境执行
4. 宿主或 IDE 返回这一轮结果
5. `My-Way` 自动补一条简短笔记
6. 如出现值得沉淀或融合的内容，生成轻量候选结论

`Prelude` 允许三种结果：

- `rewrite-light`
  - 做轻量整理
- `bypass`
  - 原话直接透传
- `observe-only`
  - 只记录，不干预执行表述

笔记至少覆盖：

- 这轮想做什么
- 实际做了什么
- 结果如何
- 是否有值得后续沉淀的点

## 7. 回合笔记生命周期

### 7.1 作用域

- `session`
  - 默认作用域；每轮短笔记先落这里
- `project`
  - 同一项目重复出现的稳定模式才可提升
- `global-candidate`
  - 只有跨项目、跨宿主或与外部反思融合高度相关的材料才进入候选层

### 7.2 保留与去重

- 每轮默认最多一条短笔记
- 重复内容应以更新摘要或折叠方式去重
- 高噪声、临时性、一次性上下文不得直接提升作用域

### 7.3 默认策略

- 先保留 `session`
- 再判断是否值得提升到 `project`
- 不直接写 `global`

## 8. 与外部反思来源的关系

### 8.1 关系定义

- 公开版统一把外部反思来源记为 `reference-system`
- `reference-system` 是 `My-Way` 的高优先级参照体，但不是绝对真源
- `My-Way` 与 `reference-system` 之间不是硬同步，不是目录覆盖，不是状态镜像
- 两者交换的单位应是“可思考的融合材料”，而不是整份运行状态

### 8.2 为什么需要反思式融合

这个需求成立的现实前提通常有两个：

- 运行时隔离：宿主环境和外部反思来源通常不共享同一运行时和同一路径
- 功能重复：两边都会做一部分整理、沉淀、护栏和工作流提炼

如果没有反思式融合，长期会产生重复建设与漂移。

### 8.3 默认融合流程

`读取变化 -> 理解变化 -> 判断价值 -> 融合或保留分歧`

### 8.4 双向方向

- `reference-system -> My-Way`
  - 外部反思来源的结构化材料作为高优先级输入
- `My-Way -> reference-system`
  - 本地长出的稳定模式可整理为上游候选，但不要求自动回写

### 8.5 v0 范围

- `v0` 必须做：融合判断、三态结论、审计记录
- `v0` 不必做：自动执行双向改写

## 9. 与其他 owner 的边界

- `My-Way`
  - 负责：常驻伴随、前置整理、后置笔记、轻量沉淀、与外部反思来源的融合判断
- `governance-owner`
  - 负责：项目治理、真源、写权边界、作用域判断、治理动作分诊
- `lifecycle-owner`
  - 负责：skill 或 agent 的生命周期、同步执行、live asset、路径、投影、打包、分发

转交规则：

- 问题变成“项目治理问题”时，转交 `governance-owner`
- 问题变成“skill/agent 生命周期或同步执行问题”时，转交 `lifecycle-owner`
- `My-Way` 可以提出融合提案或更新提案，但不默认直接执行资产级同步

### 9.1 所有权优先级矩阵

| 场景 | Primary owner | My-Way 角色 |
|---|---|---|
| 纯回合前置整理 / 回合后笔记 | `my-way` | 主责 |
| 项目真源、写权、治理边界 | `governance-owner` | 观察、转交、补笔记 |
| skill live asset、同步执行、投影、分发 | `lifecycle-owner` | 观察、转交、补笔记 |
| 外部反思内容是否值得吸收 | `my-way` | 主责判断 |
| 融合判断后需要做实际资产同步 | `lifecycle-owner` | 提案方 |
| 融合判断后影响项目治理边界 | `governance-owner` | 提案方 |

## 10. 非目标

- 不是新的 agent runtime
- 不是任意私有反思系统的镜像副本
- 不是项目总监
- 不是 skill 包管理器
- 不是大而全的自进化平台
- 不是默认直接修改全局规则、公共 skill 或外部系统本体的自动系统

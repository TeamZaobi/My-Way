---
name: my-way
description: 面向 Codex、Claude Code、AntiGravity 等 AI-Native 开发宿主环境的常驻 companion meta-skill 骨架。负责轻量 Prelude、简短 Postlude、紧凑笔记、低噪声反思 triage，以及向治理 owner 和生命周期 owner 的单写口转交。
---

# My-Way

`My-Way` 是一个始终触发的轻量 companion meta-skill 骨架，服务 `Codex`、`Claude Code`、`AntiGravity` 等 AI-Native 开发宿主环境。
它不是普通业务 skill，也不是新的 agent runtime。

## 什么时候启用

- 只要进入支持 `My-Way` 的宿主环境，就默认启用
- 不要求用户显式点名
- `always-on` 在工程上被定义为“宿主级集成契约”，不是单靠 `SKILL.md` 自动常驻

## 核心定位

- `My-Way` 是一个可移植的 companion 架构，不与任何单一私有系统强绑定
- 主职责是每轮做轻量 `Prelude + Postlude`
- 它只负责伴随、整理、留痕、融合判断，不接管项目治理和 skill 生命周期

## 不可妥协约束

- 不得静默改写用户真实意图
- 必须支持 `rewrite-light / bypass / observe-only`
- 默认只做 `proposal before mutation`
- 必须遵守单写口：治理判断让位给 `governance-owner`，skill 生命周期和同步执行让位给 `lifecycle-owner`
- 每轮最多一条短笔记，默认只落 `session`
- 不制造额外仪式感，不把每轮都扩成分析报告

## 默认回合协议

每轮按下面的顺序工作：

1. 识别这轮真实目标、硬约束和主导 owner
2. 产出一个最小 `Prelude` 决策
3. 让宿主执行主任务
4. 在回合结束后补一条短 `Postlude`
5. 只有出现稳定新模式或外部反思材料时，才进入 `fusion-review`

### 1. Prelude 决策

`Prelude` 只允许三种结果：

- `rewrite-light`
  - 用户原话存在冗余、歧义、跨工具隐含约束，或需要补出执行边界时使用
- `bypass`
  - 用户原话已经足够清楚，直接透传更安全时使用
- `observe-only`
  - 这轮不适合干预执行表述，只做观察和笔记时使用

`rewrite-light` 只允许做三件事：

- 压缩冗余，保留原意
- 补齐执行约束，避免宿主误解
- 明确这轮由谁主导：宿主、`governance-owner`、`lifecycle-owner`，还是 `My-Way` 只做伴随

`Prelude` 禁止做的事：

- 扩写成新的任务
- 改写用户目标
- 提前替用户做治理或同步决策
- 把 companion 逻辑变成对用户可见的流程噪声

### 2. Handoff 与 owner 规则

以下情况应立即切换为转交判断：

- 项目真源、写权、治理边界、作用域漂移
  - Primary owner: `governance-owner`
- skill 或 agent 的 live asset、upstream、同步执行、投影、分发
  - Primary owner: `lifecycle-owner`
- 外部反思材料是否值得吸收、保留分歧还是形成候选回流
  - Primary owner: `My-Way`

`My-Way` 的责任是识别 owner、补充上下文、留下短笔记，不替代主 owner 执行其治理权。

### 3. Postlude 规则

`Postlude` 默认只留下四类信息：

- 这轮目标
- 实际动作
- 当前结果
- 值得后续沉淀或融合的候选点

停止条件：

- 能用一条短笔记说清，就不继续扩写
- 没有稳定新模式，就不升级到 `project`
- 没有跨宿主或外部反思价值，就不进入 `global-candidate`

### 4. Reflection triage

公开版里的外部反思来源统一称为 `reference-system`。
它是高优先级参照体，但不是绝对真源。
`My-Way` 与 `reference-system` 的默认关系不是硬同步，不是目录覆盖，不是状态镜像。

只有满足下面任一条件，才触发 reflection triage：

- 外部反思来源出现新的 companion / workflow / guardrail 材料
- `My-Way` 在多个项目或多个宿主下长出稳定模式
- 本轮产生了 guardrail、workflow、companion contract 级变化

`v0` 只输出三态结论：

- `adopt`
- `diverge`
- `upstream-candidate`

`v0` 不直接执行双向改写。

## 宿主模式

- `Prompt-only`
  - 没有显式 hook 时，只做 best-effort 的轻量前后处理
- `Hook-enhanced`
  - 宿主能提供回合开始、工具返回、回合结束等信号时，执行稳定的 `Prelude + Postlude`
- `Fusion-enabled`
  - 在 `Hook-enhanced` 之上，具备外部反思交换材料输入时，才进入正式融合判断

## Fallback 约定

- 没有 hook 时，不伪造事件，只基于当前对话做最小判断
- 宿主无法稳定写笔记时，允许只保留轻量 summary
- 无法确认 owner 时，先维持 `My-Way` 伴随角色，不越权替 `governance-owner` 或 `lifecycle-owner` 决策

## 模板与参考

- 运行骨架：[runtime/README.md](./runtime/README.md)
- 输出模板：[turn-templates.md](./references/turn-templates.md)
- 需求规格：[requirements-spec.md](./references/requirements-spec.md)
- 系统架构：[system-architecture.md](./references/system-architecture.md)

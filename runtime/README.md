# My-Way Runtime Scaffold

这个目录承载 `My-Way v0` 的最小运行骨架。
它的目标不是把 `My-Way` 变成新的 agent runtime，而是把“常驻 companion 的最小机读合同”从纯文字说明里拆出来，方便后续接 hooks、脚本或宿主适配层。

## 1. 公开合同分层

这个目录只定义公开投影内部的合同分层，不宣称覆盖任何非公开部署面的完整实现。

`My-Way` 的公开合同分层固定如下：

1. `SKILL.md`
   - companion 行为合同
2. `references/`
   - 需求、架构、模板解释层
3. `runtime/schemas/`
   - 机读合同层
4. `runtime/hosts/`
   - 宿主适配层
5. `runtime/examples/`
   - 样例 artifact，不是真源

约束：

- 运行时日志和可变状态默认不落回仓库真源
- `runtime/examples/` 只用于说明结构，不承担控制权
- 高影响动作仍停留在提案层，不在这里直接赋予 mutation 权

## 2. v0 固定 artifact

当前固定三类机读 artifact：

1. `turn.events.jsonl`
   - append-only 事件流
2. `turn.note.json`
   - 每轮最多一条短笔记的实例结构
3. `reflection.exchange.packet.json`
   - 外部反思交换包

## 3. 当前目录职责

### 3.1 `schemas/`

冻结最小字段、枚举和附加字段边界：

- `turn-event.schema.json`
- `turn-note.schema.json`
- `reflection-exchange-packet.schema.json`

### 3.2 `hosts/`

按宿主拆薄适配说明：

- `codex.md`
- `claude-code.md`
- `antigravity.md`

这些文档只说明：

- 默认运行模式
- 可观察信号如何映射到 `Prelude / Execute / Postlude / Fusion`
- 何时必须降级到 `Prompt-only`
- 何时必须转交 `governance-authority` / `lifecycle-authority`

### 3.3 `examples/`

提供最小样例 payload，方便：

- 写 smoke checker
- 写 hook adapter
- 做 drift audit

### 3.4 `bridge/`

承载 reflection bridge 的审计合同，而不是新的路由系统：

- `README.md`
  - triage 输入、输出、跳过条件、owner 约束
- `reflection-triage-audit.schema.json`
  - 审计记录 schema
- `examples/reflection-triage-audit.jsonl`
  - 可回放的最小 triage 样例
- `replay-review.md`
  - 回放和复核协议

### 3.5 `guardrails/`

承载轻量护栏的合同、初始状态和审计样例：

- `guardrails.contract.json`
  - 阈值、路径边界、review gate 条件
- `guardrails.state.json`
  - 最小运行态模板
- `guardrails.events.jsonl`
  - 追加式审计样例

### 3.6 `../scripts/`

当前已经补齐最小脚本面：

- `myway_runtime.py`
  - 写入 turn event / turn note / reflection packet，并生成 triage audit
- `myway_validate.py`
  - 校验 schema、样例和 guardrails 资产
- `myway_smoke.py`
  - 用样例跑通最小端到端 smoke
- `enforce_guardrails.py`
  - 执行 anti-loop / cooldown / review gate / mutation control
- `schema_utils.py`
  - 共享 JSON/JSONL/最小 schema 工具

## 4. 命名与边界

命名约束：

- schema 文件统一用 `*.schema.json`
- 样例实例文件统一用 `*.json` 或 `*.jsonl`
- 宿主文档只写适配层，不重写核心语义

边界约束：

- `My-Way` 的核心语义只认 `SKILL.md + references/ + runtime/schemas/`
- `hosts/` 不得发明新的核心 owner
- `examples/` 不得引入 schema 之外的字段漂移
- reflection triage 在 `v0` 仍然只有 `adopt / diverge / upstream-candidate`

兼容说明：

- serialized examples 和 schema 中仍可能保留 `governance-owner`、`lifecycle-owner`、`global-candidate` 等兼容标签
- 对外文档语义以 `governance-authority`、`lifecycle-authority`、`cross-host candidate` 为准

## 5. 接入顺序

推荐接入顺序：

1. 先用 `Prompt-only` 跑通 `Prelude + Postlude`
2. 再把宿主的开始/结束或工具返回信号接到事件流
3. 再补 reflection triage 的交换包
4. 最后再接更细的 guardrails 和自动化发布流程

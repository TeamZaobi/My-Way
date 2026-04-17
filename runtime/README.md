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

当前固定三类公共 artifact，加上三类 carry-forward sidecar artifact：

1. `turn.events.jsonl`
   - append-only 事件流
2. `turn.note.json`
   - 每轮最多一条短笔记的实例结构
3. `turn.carryforward.candidate.json`
   - `Postlude` 之后派生的耐久 carry-forward 候选，用来分类稳定偏好、方法模式、capability mount 规则等耐久信号
4. `reflection.exchange.packet.json`
   - 外部反思交换包
5. `carryforward.store.jsonl`
   - durable carry-forward record store；对 promoted candidate 做 upsert / merge
6. `turn.carryforward.recall.json`
   - 新 turn 进入前生成的 bounded recall plan

说明：

- `turn.carryforward.candidate.json` 不是个人记忆系统
- `carryforward.store.jsonl` 是 durable context store，不是原始追加日志
- `turn.carryforward.recall.json` 只承接 recall 结果，不承接隐藏记忆本体
- 它只是一个可选 sidecar，用来承接可复用的耐久上下文
- 私有部署可以把它映射到自己的长期状态系统，但公开合同本身不承诺任何隐藏记忆语义

## 3. 当前目录职责

### 3.1 `schemas/`

冻结最小字段、枚举和附加字段边界：

- `turn-event.schema.json`
- `turn-note.schema.json`
- `turn-carryforward-candidate.schema.json`
- `carryforward-record.schema.json`
- `turn-carryforward-recall.schema.json`
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
- 验证 note 与 carry-forward sidecar 不混写
- 验证 method pattern / capability mount rule 会被正确识别
- 验证 durable carry-forward store 的 upsert / provenance / bounded recall 正常工作

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
  - 写入 turn event / turn note / carry-forward candidate / reflection packet，并生成 triage audit
  - `carry-forward candidate` 会对稳定偏好、方法模式、capability mount 规则、routing 规则和外部经验做最小分类
  - `consolidate-carryforward` 会把 promoted candidate 合并成 durable carry-forward record
  - `recall-carryforward` 会生成只服务当前 turn 的 bounded recall plan
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

1. 先用 `Prompt-only` 跑通 turn 前的 bounded recall、意图翻译、方法层和能力挂载层最小判断
2. 再在 `Postlude` 后补 `carry-forward candidate`
3. 再把 promoted candidate 合并进 durable carry-forward store
4. 再把宿主的开始/结束或工具返回信号接到事件流
5. 再补 reflection triage 的交换包
6. 最后再接更细的 guardrails 和自动化发布流程

## 6. 当前命令面

最小命令面如下：

```bash
python scripts/myway_validate.py bundle
python scripts/myway_smoke.py
python scripts/myway_runtime.py finalize-turn --input-json /path/to/postlude.note.json --note-path /path/to/turn.note.json --history-path /path/to/turn.notes.history.jsonl --candidate-path /path/to/turn.carryforward.candidate.json --carryforward-log-path /path/to/turn.carryforward.log.jsonl
python scripts/myway_runtime.py write-carryforward-candidate --note-path runtime/examples/turn.note.json --candidate-path runtime/examples/turn.carryforward.candidate.json
python scripts/myway_runtime.py consolidate-carryforward --candidate-path runtime/examples/turn.carryforward.candidate.json --carryforward-store-path runtime/examples/carryforward.store.jsonl
python scripts/myway_runtime.py recall-carryforward --input-json /path/to/turn.recall.input.json --carryforward-store-path runtime/examples/carryforward.store.jsonl --output-path runtime/examples/turn.carryforward.recall.json
python scripts/myway_runtime.py triage-packet --packet-path runtime/examples/reflection.exchange.packet.json --audit-path runtime/bridge/examples/reflection-triage-audit.jsonl --turn-id turn_2026_04_17_001 --events-path runtime/examples/turn.events.jsonl --note-path runtime/examples/turn.note.json
```

如果宿主要把“回合结束”接成一个稳定 hook，优先调用 `finalize-turn`：

- 输入仍然是一份 `turn.note` 结构的 JSON
- 命令会先写 `turn.note.json`
- 然后立即派生 `turn.carryforward.candidate.json`
- 派生阶段会把稳定信号分类到 preference / method-pattern / capability-mount-rule / routing-rule / external-pattern 等类型
- 如果提供 `--carryforward-log-path`，再把 `carry-forward` 结论追加到外部可写日志
- 如果提供 `--carryforward-store-path`，再把 promoted candidate 合并到 durable carry-forward store

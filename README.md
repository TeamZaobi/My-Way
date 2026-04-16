# My-Way

`My-Way` 是一个公开的、可移植的 `always-on companion meta-skill` 骨架。
它服务于 `Codex`、`Claude Code`、`AntiGravity` 等 AI-Native 开发宿主环境，用最小运行合同把下面几件事稳定下来：

- 每轮轻量 `Prelude`
- 每轮简短 `Postlude`
- append-only 事件层与短笔记层
- 与外部反思来源的可审计 triage
- 低噪声、可验证的 guardrails

这个公开版只保留架构和技术实现。
它不包含个人记忆、私有路由命名、真实运行状态、宿主密钥或任何个性化配置。

## 仓库边界

- 公开版保留：协议、schema、样例、验证脚本、smoke、宿主适配说明
- 公开版去掉：个人工作流命名、私有 owner 体系、真实记忆和内部系统直连
- 运行时可变状态默认不应直接提交回仓库

## 目录结构

```text
My-Way/
├── SKILL.md
├── references/
│   ├── requirements-spec.md
│   ├── system-architecture.md
│   └── turn-templates.md
├── runtime/
│   ├── README.md
│   ├── bridge/
│   ├── examples/
│   ├── guardrails/
│   ├── hosts/
│   └── schemas/
└── scripts/
```

## 公开版 owner 模型

为避免把私有工作流命名当成公共接口，这里只保留 3 个通用 owner：

- `my-way`
  - companion 本体
- `governance-owner`
  - 项目治理、真源、写权和范围边界
- `lifecycle-owner`
  - skill/agent 生命周期、同步执行、发布和分发

## 快速验证

```bash
python scripts/myway_validate.py bundle
python scripts/myway_smoke.py
```

如果你要把它接到真实宿主里，先从 `Prompt-only` 跑通，再逐步接入 `Hook-enhanced` 和 `Fusion-enabled`。

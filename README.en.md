# ShipKit · 舰桥

[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-compatible-orange)](https://docs.anthropic.com/en/docs/claude-code)

> 舰桥 (jiàn qiáo) — the command bridge of a ship. An AI engineering workflow that turns team conventions into Claude Code configuration, so AI follows your rules from idea to delivery.

English | [简体中文](README.md)

---

## Quick Start

### Prerequisites

- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code)
- Python 3

### Install

```bash
git clone https://github.com/<your-username>/shipkit.git
cd shipkit
claude
```

In Claude Code, type:

```
按 SETUP.md 执行安装
```

AI will execute the full installation automatically — backing up existing config, copying files, merging settings, and verifying everything.

### Verify

Open Claude Code in any directory and type:

```
fix a typo in the README
```

Watch AI automatically route to quick-fix-flow.

---

## What is ShipKit?

ShipKit is a Claude Code configuration system organized in four layers:

```
┌──────────────────────────────────────────┐
│  Constraint Layer — CLAUDE.md + rules/   │
│  Engineering standards for AI to follow  │
├──────────────────────────────────────────┤
│  Orchestration Layer — skills/ + profiles/│
│  Risk-based workflow routing             │
├──────────────────────────────────────────┤
│  Execution Layer — agents/ (16 agents)   │
│  Specialist agents for design & review   │
├──────────────────────────────────────────┤
│  Guard Layer — hooks/ (4 Python hooks)   │
│  Hard enforcement of safety rules        │
└──────────────────────────────────────────┘
```

**Core principles**: role-based checkpoints, AI-document-first, independent verification, evidence-driven decisions.

---

## Workflows

| Intent | Workflow | Profile |
|--------|----------|---------|
| New feature, product change | `product-to-test-flow` | standard |
| Security, money, migration | `strict-product-to-test-flow` | strict |
| Small bug, narrow fix | `quick-fix-flow` | minimal |
| Build/test error | `build-fix-flow` | — |
| Code review | `review-flow` | — |

The full `product-to-test-flow` runs through 12 phases: requirement → PRD → engineering spec → research → backend/frontend design → contract → plan → coding (TDD) → verification → review → delivery → archive.

---

## Profiles

| | minimal | standard | strict |
|---|---------|----------|--------|
| Scope | Small bugs, ≤3 files | Normal features | Auth, money, data migration |
| Checkpoints | None | 3 (prd, spec, plan) | 3 + contract + rollback |
| Verification | Targeted test only | Full coverage + tests | + security/DB/revert checks |

---

## Agents

16 specialist agents in four categories:

- **Designers** — produce design docs (PRD, specs, architecture, contracts, plans)
- **Reviewers** — review code, Java, database, security, frontend UX
- **Resolvers** — fix build/test errors within allowed scope
- **Curator** — extract reusable lessons post-delivery

---

## Customization

See the full [简体中文 README](README.md) for detailed customization guides including how to adjust agents, profiles, hooks, and project-level engineering governance.

---

## License

MIT

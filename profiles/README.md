# Profiles

Profiles decide how much role-based workflow is required.

## minimal

Small bugs and narrow changes. It is fast, but still requires code evidence, `07_实施计划.md`, `10_自查报告.md`, `CHANGE_METRICS.json`, and `09_验证结果.md`.

Upgrade out of minimal when the change touches permissions, transactions/concurrency, external systems, database, API contracts, both frontend and backend, unclear product semantics, or more than three files.

## standard

Default product-to-test flow. It uses role checkpoints:

- `prd_confirmation`
- `engineering_spec_confirmation`
- `backend_design_confirmation` when backend is affected
- `frontend_design_confirmation` when frontend is affected
- `contract_confirmation` when API/data contract is affected
- `plan_confirmation`

## strict

High-risk flow for security, money, orders, inventory, migrations, concurrency, external integrations, files, webhooks, sensitive data, or irreversible operations.

Strict requires engineering spec, contract, implementation plan, rollback/compat strategy, security/DB review when applicable, and recorded verification evidence.

## learning

Post-delivery learning. It consumes delivery docs and metrics, then produces `13_经验沉淀.md` and `14_Agent评估.md`.

## Optional Project Consistency

Project-level consistency governance is a pluggable enhancement:

- No `openspec/specs/engineering/engineering.json`: Base Flow.
- `enabled=true, mode=advisory`: record enhanced risks, do not block.
- `enabled=true, mode=enforced`: enhanced checks may block review/archive.

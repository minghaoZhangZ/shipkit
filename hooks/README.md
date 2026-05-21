# Hooks

PreToolUse hooks that provide hard enforcement of workflow guardrails.

## Implemented

### Phase 1: Safety (done)

- `dangerous-command-guard.py` — blocks destructive commands (git reset --hard, push --force, rm -rf, DROP TABLE, curl|sh, etc.)
- `checkpoint-guard.py` — blocks business code edits and build commands when user confirmation is pending (reads .workflow_state)
- `scope-guard.py` — blocks edits to files outside the implementation plan's allowed scope (active in coding/verification phases)
- `canonical-filename-guard.py` — blocks non-canonical filenames under openspec/changes/*/
- `engine-guard.py` — validates rule ID prefixes when writing openspec/specs/engineering/**/*.md against engineering.json rulePrefixIndex

### How they work

All three are PreToolUse hooks registered in `~/.claude/settings.json`. They receive tool call JSON on stdin, check against workflow state, and:

- **exit 0** = allow
- **exit 2** = hard block (stderr is fed back to Claude so it can self-correct)

### Dependencies

- Python 3 (standard library only, no pip packages needed)

### Workflow integration

These hooks depend on `.workflow_state` files maintained by the workflow skills:

- `product-to-test-flow` — standard/strict profiles update state at each checkpoint
- `quick-fix-flow` — minimal profile also maintains state
- `strict-product-to-test-flow` — inherits from product-to-test-flow

Key state fields hooks read:

- `requires_user_confirmation` — if "true", checkpoint guard activates
- `user_confirmed` — if "false", business code edits are blocked
- `current_phase` — scope guard only activates in "coding" and "verification"

If an active `.workflow_state` exists but these core fields are missing,
empty, or invalid, checkpoint/scope guards fail closed for business-code
operations. Writing AI documents under `openspec/changes/*/` remains
allowed so the workflow state can be repaired.

Project-level consistency governance is intentionally **not** required by these hooks.

- If a project has no `openspec/specs/engineering/engineering.json`, hooks continue to enforce only Base Flow safety.
- Future architecture guards must be optional: no manifest means `exit 0`; `mode=advisory` means report only; `mode=enforced` may block only deterministic rules.

## Roadmap

### Phase 2: Quality

- `java-light-quality-gate.py` — scan for System.out.println, printStackTrace, empty catch after Java edits
- `test-result-check.py` — verify test results are recorded before claiming completion

### Phase 3: Learning

- `project-observe.py` — record project-level experience signals
- `promotion-candidate.py` — detect repeatable patterns worth promoting to rules/skills/agents

## Design principles

- Hooks do deterministic checks only.
- Judgement-based findings go to `<change-dir>/13_LESSONS_LEARNED.md` for new changes; old changes may keep `12_LESSONS_LEARNED.md`.
- No full Maven/Gradle builds triggered automatically.
- Keep scripts lightweight (<1s execution).

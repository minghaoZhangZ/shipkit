---
name: copy-polish-zh
description: Use when polishing Chinese user-facing copy, release notes, requirement summaries, empty states, error messages, confirmation dialogs, help text, or delivery documents for a more natural human tone.
---

# Copy Polish Zh

Use this skill for Chinese text quality only. It may improve clarity, tone, and readability, but must not change product meaning, API semantics, code behavior, test assertions, or legal/security wording.

## Suitable Text

- UI labels, empty states, error messages, toast/dialog copy.
- Release notes, delivery summaries, requirement summaries.
- Help text, onboarding text, operation hints.
- Review comments when tone should be direct but not stiff.

## Rules

- Keep technical meaning exact.
- Prefer concise, natural Chinese over marketing language.
- Keep nouns consistent with the product and existing code.
- Preserve IDs, route names, API fields, enum values, command names, file paths, and error codes.
- Preserve severity and operational risk; do not soften warnings that affect safety, money, permission, data, or compliance.
- Do not rewrite code comments unless the request explicitly targets comments.

## Output Pattern

For each changed text, provide:

```text
原文: ...
建议: ...
原因: 更自然 / 更明确 / 更短 / 风险表达更准确
```

When editing files, only touch the text explicitly in scope and keep unrelated formatting unchanged.

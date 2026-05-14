#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate role-checkpoint workflow wiring.

This script is intentionally read-only for repository files. It checks:
- hook Python files compile
- profile skill/agent references exist
- required role-checkpoint skills exist
- old English AI document names only appear in compatibility contexts
- checkpoint/scope hooks block or allow representative tool calls
"""

import json
import py_compile
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_SKILLS = {
    'product-to-test-flow',
    'prd-check-flow',
    'engineering-spec-flow',
    'backend-design-check-flow',
    'frontend-design-check-flow',
    'contract-check-flow',
    'implementation-plan-check-flow',
    'quick-fix-flow',
    'strict-product-to-test-flow',
    'verification-flow',
    'review-flow',
    'openspec-archive-change',
}

OLD_DOC_NAMES = [
    '00_REQUIREMENT.md',
    '01_PRODUCT_DISCOVERY.md',
    '02_SPEC.md',
    '03_CODEBASE_RESEARCH.md',
    '04_BACKEND_DESIGN.md',
    '05_FRONTEND_DESIGN.md',
    '06_DATA_CONTRACT.md',
    '07_IMPLEMENTATION_PLAN.md',
    '08_TEST_PLAN.md',
    '09_TEST_RESULT.md',
    '10_SELF_REVIEW.md',
    '11_REVIEW_REPORT.md',
    '12_RELEASE_NOTE.md',
    '13_LESSONS_LEARNED.md',
    '14_AGENT_EVAL.md',
]

COMPAT_MARKERS = ('兼容', '旧', 'old', 'compat', 'fallback', 'alias')


def fail(message):
    print(f'[FAIL] {message}')
    sys.exit(1)


def ok(message):
    print(f'[OK] {message}')


def warn(message):
    print(f'[WARN] {message}')


def skill_exists(name):
    return (ROOT / 'skills' / name / 'SKILL.md').is_file()


def agent_exists(name):
    return (ROOT / 'agents' / f'{name}.md').is_file()


def check_hooks_compile():
    for rel in ('hooks/checkpoint-guard.py', 'hooks/scope-guard.py', 'hooks/dangerous-command-guard.py'):
        py_compile.compile(str(ROOT / rel), doraise=True)
    ok('hook Python files compile')


def check_profiles():
    data = json.loads((ROOT / 'profiles' / 'profiles.json').read_text(encoding='utf-8'))
    for profile_name, profile in data['profiles'].items():
        for field in ('requiredSkills', 'optionalSkills'):
            for skill in profile.get(field, []):
                if not skill_exists(skill):
                    fail(f'profile {profile_name} references missing skill: {skill}')
        for field in ('requiredAgents', 'optionalAgents'):
            for agent in profile.get(field, []):
                if not agent_exists(agent):
                    fail(f'profile {profile_name} references missing agent: {agent}')
    ok('profiles reference existing skills and agents')


def check_required_skills():
    missing = [name for name in sorted(REQUIRED_SKILLS) if not skill_exists(name)]
    if missing:
        fail(f'missing required skills: {", ".join(missing)}')
    ok('required role-checkpoint skills exist')


def check_old_doc_refs_are_compat():
    paths = list((ROOT / 'skills').glob('**/SKILL.md')) + list((ROOT / 'agents').glob('*.md'))
    violations = []
    for path in paths:
        lines = path.read_text(encoding='utf-8').splitlines()
        for lineno, line in enumerate(lines, start=1):
            if any(name in line for name in OLD_DOC_NAMES):
                if line.strip().startswith('|'):
                    continue
                start = max(0, lineno - 8)
                context = '\n'.join(lines[start:lineno + 1])
                if not any(marker in context for marker in COMPAT_MARKERS):
                    violations.append(f'{path.relative_to(ROOT)}:{lineno}: {line.strip()}')
    if violations:
        fail('old document names outside compatibility context:\n' + '\n'.join(violations[:20]))
    ok('old document names only appear in compatibility contexts')


def run_hook(hook_path, payload, cwd):
    proc = subprocess.run(
        [sys.executable, str(ROOT / hook_path)],
        input=json.dumps(payload, ensure_ascii=False),
        text=True,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return proc.returncode, proc.stdout, proc.stderr


def write_state(ai_dir, confirmed=False, checkpoint='prd_confirmation', phase='prd', state='active'):
    ai_dir.joinpath('.workflow_state').write_text(
        '\n'.join([
            'schema_version: "1.0"',
            'change_id: demo',
            'profile: standard',
            f'current_phase: {phase}',
            f'state: {state}',
            f'checkpoint: {checkpoint}',
            f'requires_user_confirmation: {"false" if confirmed else "true"}',
            f'user_confirmed: {"true" if confirmed else "false"}',
            'confirmation_type: approve_prd',
            'confirmation_role: product_owner',
            'confirmation_docs: ["01_PRD产品需求.md"]',
            'confirmed_checkpoints: []',
            'required_checkpoints: ["prd_confirmation"]',
            'affected_areas: ["frontend"]',
            'context_package: "CONTEXT_PACKAGE.md"',
            'trace_matrix_status: pending',
        ]),
        encoding='utf-8',
    )


def check_hook_behavior():
    tmp_base = ROOT / 'scripts' / 'tmp-validation'
    tmp_base.mkdir(exist_ok=True)
    tmp = tmp_base / 'workspace'
    shutil.rmtree(tmp, ignore_errors=True)
    ai_dir = tmp / 'openspec' / 'changes' / 'demo' / 'ai'
    ai_dir.mkdir(parents=True, exist_ok=True)
    (tmp / 'src').mkdir(exist_ok=True)
    (tmp / 'src' / 'App.java').write_text('class App {}\n', encoding='utf-8')
    (tmp / 'README.md').write_text('# demo\n', encoding='utf-8')

    write_state(ai_dir, confirmed=False, checkpoint='prd_confirmation', phase='prd')
    payload = {'tool_name': 'Edit', 'cwd': str(tmp), 'tool_input': {'file_path': str(tmp / 'src' / 'App.java')}}
    code, _, _ = run_hook('hooks/checkpoint-guard.py', payload, tmp)
    if code != 2:
        fail('checkpoint-guard did not block business edit during prd_confirmation')

    payload['tool_input']['file_path'] = str(ai_dir / '01_PRD产品需求.md')
    code, _, _ = run_hook('hooks/checkpoint-guard.py', payload, tmp)
    if code != 0:
        fail('checkpoint-guard blocked AI doc write during pending confirmation')

    write_state(ai_dir, confirmed=False, checkpoint='frontend_design_confirmation', phase='frontend_design')
    payload = {'tool_name': 'Bash', 'cwd': str(tmp), 'tool_input': {'command': 'npm run build'}}
    code, _, _ = run_hook('hooks/checkpoint-guard.py', payload, tmp)
    if code != 2:
        fail('checkpoint-guard did not block build command during frontend_design_confirmation')

    write_state(ai_dir, confirmed=True, checkpoint='plan_confirmation', phase='plan')
    code, _, _ = run_hook('hooks/checkpoint-guard.py', payload, tmp)
    if code != 0:
        fail('checkpoint-guard blocked build command after confirmation')

    write_state(ai_dir, confirmed=True, checkpoint='plan_confirmation', phase='coding')
    (ai_dir / '07_实施计划.md').write_text(
        '# 实施计划\n\n## 7. 允许修改的文件范围\n\n- src/**\n\n## 8. 不允许修改的文件\n',
        encoding='utf-8',
    )
    payload = {'tool_name': 'Edit', 'cwd': str(tmp), 'tool_input': {'file_path': str(tmp / 'src' / 'App.java')}}
    code, _, _ = run_hook('hooks/scope-guard.py', payload, tmp)
    if code != 0:
        fail('scope-guard blocked file inside allowed scope')

    payload['tool_input']['file_path'] = str(tmp / 'README.md')
    code, _, _ = run_hook('hooks/scope-guard.py', payload, tmp)
    if code != 2:
        fail('scope-guard did not block file outside allowed scope')

    # --- state=blocked 阻断测试 ---
    write_state(ai_dir, confirmed=True, checkpoint='plan_confirmation', phase='coding', state='blocked')
    payload = {'tool_name': 'Edit', 'cwd': str(tmp), 'tool_input': {'file_path': str(tmp / 'src' / 'App.java')}}
    code, _, _ = run_hook('hooks/checkpoint-guard.py', payload, tmp)
    if code != 2:
        fail('checkpoint-guard did not block business edit when state=blocked')

    # AI 文档在 blocked 状态下仍可写
    payload['tool_input']['file_path'] = str(ai_dir / 'PENDING_DECISIONS.md')
    code, _, _ = run_hook('hooks/checkpoint-guard.py', payload, tmp)
    if code != 0:
        fail('checkpoint-guard blocked AI doc write when state=blocked')

    # --- state=failed 阻断测试 ---
    write_state(ai_dir, confirmed=True, checkpoint='plan_confirmation', phase='coding', state='failed')
    payload = {'tool_name': 'Edit', 'cwd': str(tmp), 'tool_input': {'file_path': str(tmp / 'src' / 'App.java')}}
    code, _, _ = run_hook('hooks/checkpoint-guard.py', payload, tmp)
    if code != 2:
        fail('checkpoint-guard did not block business edit when state=failed')

    ok('checkpoint and scope hook behavior checks pass')
    shutil.rmtree(tmp, ignore_errors=True)


def check_settings_local_dangerous_allow():
    path = ROOT / 'settings.local.json'
    if not path.is_file():
        return
    text = path.read_text(encoding='utf-8')
    patterns = ('rm -rf', 'Remove-Item', 'DROP TABLE', '--no-verify', 'git reset --hard', 'git checkout --', 'git clean -f')
    hits = [pat for pat in patterns if pat in text]
    if hits:
        warn('settings.local.json contains dangerous allow entries; dangerous-command-guard should still block them, but cleanup is recommended: ' + ', '.join(hits))


def main():
    check_hooks_compile()
    check_required_skills()
    check_profiles()
    check_old_doc_refs_are_compat()
    check_hook_behavior()
    check_settings_local_dangerous_allow()
    ok('role-checkpoint workflow validation complete')


if __name__ == '__main__':
    main()

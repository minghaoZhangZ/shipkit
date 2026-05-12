#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PreToolUse hook: block destructive bash/powershell commands before execution.

Reads tool call JSON from stdin. Only processes Bash tools.
Exit 0 = allow, Exit 2 = hard block (stderr goes back to Claude).
"""

import sys
import json
import re

# Patterns that are ALWAYS blocked regardless of phase.
# Each is a (regex, description) pair.
DENY_PATTERNS = [
    # Git destructive
    (r'git\s+reset\s+--hard', 'git reset --hard: discards all local changes'),
    (r'git\s+push\s+.*(--force|-f)', 'git push --force: overwrites remote history'),
    (r'git\s+checkout\s+--\s', 'git checkout -- <file>: discards file changes'),
    (r'git\s+clean\s+-f', 'git clean -f: deletes untracked files'),
    # Unix rm -rf any target (not just root)
    (r'\brm\s+-rf\b', 'rm -rf: recursive force delete'),
    (r'\brm\s+-fr\b', 'rm -fr: recursive force delete'),
    # Windows destructive delete (any param order)
    (r'Remove-Item.*(-Recurse.*-Force|-Force.*-Recurse)', 'Remove-Item -Recurse -Force: recursive force delete'),
    (r'\brmdir\s+/s\b', 'rmdir /s: recursive directory delete'),
    (r'\bdel\s+/f\s+/s\b', 'del /f /s: force recursive file delete'),
    (r'\bdel\s+/s\s+/f\b', 'del /s /f: force recursive file delete'),
    # Windows diskpart/format
    (r'\bformat\s+[A-Za-z]:', 'format <drive>: disk format'),
    (r'\bdiskpart\b', 'diskpart: disk partition tool'),
    # Skip git hooks
    (r'--no-verify', '--no-verify: skip git hooks'),
    (r'--no-gpg-sign', '--no-gpg-sign: skip GPG signing'),
    # Database destructive
    (r'\bDROP\s+TABLE\b', 'DROP TABLE: irreversible table deletion'),
    (r'\bDROP\s+DATABASE\b', 'DROP DATABASE: irreversible database deletion'),
    (r'\bTRUNCATE\s+TABLE\b', 'TRUNCATE TABLE: irreversible table truncation'),
    # Curl/wget pipe shell (RCE)
    (r'curl\s+.*\|\s*(ba)?sh', 'curl | sh: remote code execution risk'),
    (r'wget\s+.*\|\s*(ba)?sh', 'wget | sh: remote code execution risk'),
    # PowerShell destructive
    (r'Clear-RecycleBin', 'Clear-RecycleBin: clear recycle bin'),
    (r'Remove-Partition', 'Remove-Partition: remove disk partition'),
]


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, IOError):
        sys.exit(0)

    tool_name = data.get('tool_name', '')
    if tool_name != 'Bash':
        sys.exit(0)

    command = data.get('tool_input', {}).get('command', '')
    if not command:
        sys.exit(0)

    for pattern, description in DENY_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            print(
                f"\n[DangerousCommandGuard] Blocked dangerous command\n"
                f"  Command: {command}\n"
                f"  Reason: {description}\n"
                f"  To proceed, run this command manually in a terminal.\n",
                file=sys.stderr,
            )
            sys.exit(2)

    sys.exit(0)


if __name__ == '__main__':
    main()

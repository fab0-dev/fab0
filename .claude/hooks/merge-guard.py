#!/usr/bin/env python3
# from fab0-dev/fab0-examples story--v0.2.0
"""The merge guard: a Claude Code PreToolUse hook on Bash. It blocks commands the model issues that would merge
a pull request, push to the base branch, or force-push. fab0's `apply` merges what a gate allows, through its own
git calls, and people merge on GitHub; neither passes through this hook.

The base branch is `git.base` in .fab0/fab0.yaml (default `main`). Exit 2 blocks the command and tells the model
why; exit 0 lets it run.
"""

import json
import os
import re
import shlex
import sys
from pathlib import Path


def base_branch() -> str:
    project = Path(os.environ.get("CLAUDE_PROJECT_DIR", "."))
    try:
        text = (project / ".fab0" / "fab0.yaml").read_text()
    except OSError:
        return "main"
    found = re.search(r"^\s*base:\s*['\"]?([\w./-]+)", text, re.M)
    return found.group(1) if found else "main"


def segments(command: str) -> list[list[str]]:
    """The simple commands of a command line, as words."""
    out = []
    for part in re.split(r"&&|\|\||[;|\n]|\$\(|`", command):
        try:
            words = shlex.split(part)
        except ValueError:
            words = part.split()
        while words and ("=" in words[0] and not words[0].startswith("-") or words[0] in ("sudo", "env", "command")):
            words = words[1:]  # VAR=value prefixes and wrappers
        if words:
            out.append(words)
    return out


def why_blocked(words: list[str], base: str) -> str | None:
    if words[0] == "gh" and words[1:3] == ["pr", "merge"]:
        return "merging a pull request is a person's decision, or `fab0-resolve apply`'s within the merge policy"
    if words[0] == "gh" and len(words) > 1 and words[1] == "api" and any(re.search(r"/merges?\b", w) for w in words):
        return "merging through the API is a person's decision, or `fab0-resolve apply`'s"
    if words[0] != "git" or "push" not in words:
        return None
    args = words[words.index("push") + 1 :]
    if any(a in ("-f", "--force", "--mirror") or a.startswith("--force") for a in args):
        return "nothing in a fab0 project is force-pushed"
    for arg in args:
        if arg.startswith("+"):
            return "nothing in a fab0 project is force-pushed"
        target = arg.split(":")[-1].removeprefix("refs/heads/")
        if target == base and not arg.startswith("-"):
            return f"nothing is pushed to {base} directly; a person merges the run's pull request"
    return None


def main() -> int:
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return 0
    if event.get("tool_name") != "Bash":
        return 0
    command = (event.get("tool_input") or {}).get("command", "")
    base = base_branch()
    for words in segments(command):
        reason = why_blocked(words, base)
        if reason:
            print(f"Blocked by the merge guard: {reason}.", file=sys.stderr)
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())

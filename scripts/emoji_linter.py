#!/usr/bin/env python3
"""
emoji_linter.py - Zero-Emoji Policy Enforcer for /swarm.
Audits files, directories, git diffs, and text streams to ensure zero emojis
are present in code, comments, docstrings, or documentation.
Zero-Emoji Policy Enforced.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Comprehensive regex matching Unicode emojis and pictographs without false positives on box-drawing characters
EMOJI_PATTERN = re.compile(
    r"[\U0001F600-\U0001F64F"  # Emoticons
    r"\U0001F300-\U0001F5FF"  # Misc Symbols and Pictographs
    r"\U0001F680-\U0001F6FF"  # Transport and Map
    r"\U0001F700-\U0001F77F"  # Alchemical Symbols
    r"\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
    r"\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
    r"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
    r"\U0001FA00-\U0001FA6F"  # Chess Symbols
    r"\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
    r"\U0001F1E6-\U0001F1FF"  # Regional Indicator Symbols (Flags)
    r"\U0001F200-\U0001F251"  # Enclosed Ideographic Supplement
    r"\u2702-\u27B0"          # Dingbats
    r"\u2600-\u26FF"          # Misc Symbols
    r"\u231A-\u231B\u23E9-\u23EC\u23F0\u23F3"  # Misc Technical Emojis
    r"\u2B50-\u2B55"          # Star symbols
    r"\u200D"                  # Zero Width Joiner
    r"\uFE0F"                  # Variation Selector-16
    r"]"
)

IGNORED_DIRS = {
    ".git", ".svn", ".hg", "__pycache__", "node_modules", "target", "dist",
    "build", ".venv", "venv", ".idea", ".vscode", ".pytest_cache"
}

IGNORED_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".woff", ".woff2",
    ".ttf", ".eot", ".zip", ".tar", ".gz", ".pyc", ".bin", ".lock"
}


def scan_text(content: str, source_name: str = "") -> List[Dict[str, Any]]:
    violations = []
    lines = content.splitlines()
    for line_no, line in enumerate(lines, start=1):
        matches = EMOJI_PATTERN.findall(line)
        if matches:
            violations.append({
                "source": source_name,
                "line": line_no,
                "content": line.strip()[:100],
                "emojis": matches
            })
    return violations


def scan_file(filepath: Path) -> List[Dict[str, Any]]:
    if filepath.suffix.lower() in IGNORED_EXTENSIONS:
        return []
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        return scan_text(content, str(filepath))
    except Exception:
        return []


def scan_directory(root_dir: Path) -> List[Dict[str, Any]]:
    all_violations = []
    for root, dirs, files in os.walk(root_dir):
        # Prune ignored directories
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        for file in files:
            p = Path(root) / file
            violations = scan_file(p)
            all_violations.extend(violations)
    return all_violations


def scan_git_diff(cwd: Path) -> List[Dict[str, Any]]:
    try:
        proc = subprocess.run(
            ["git", "diff", "HEAD"],
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if proc.returncode != 0:
            # Fallback to unstaged diff
            proc = subprocess.run(
                ["git", "diff"],
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
        diff_text = proc.stdout
        added_lines = []
        for line in diff_text.splitlines():
            if line.startswith("+") and not line.startswith("+++"):
                added_lines.append(line[1:])
        return scan_text("\n".join(added_lines), source_name="git_diff")
    except Exception:
        return []


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Zero-Emoji Policy Auditor for /swarm."
    )
    parser.add_argument("paths", nargs="*", default=["."], help="Files or directories to audit (default: .)")
    parser.add_argument("--diff", action="store_true", help="Audit git diff changes only")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")

    args = parser.parse_args()
    violations: List[Dict[str, Any]] = []

    if args.diff:
        violations.extend(scan_git_diff(Path(".").resolve()))
    else:
        for p_str in args.paths:
            p = Path(p_str).resolve()
            if p.is_file():
                violations.extend(scan_file(p))
            elif p.is_dir():
                violations.extend(scan_directory(p))

    passed = len(violations) == 0

    if args.json:
        print(json.dumps({"passed": passed, "total_violations": len(violations), "violations": violations}, indent=2))
    else:
        if passed:
            print("[OK] Zero-Emoji Audit Passed. 100% compliant.")
            sys.exit(0)
        else:
            print(f"[BLOCKER] Zero-Emoji Policy Violated! Found {len(violations)} emojis:")
            for v in violations:
                print(f"  {v['source']}:{v['line']} -> {v['emojis']} in '{v['content']}'")
            sys.exit(1)


if __name__ == "__main__":
    main()

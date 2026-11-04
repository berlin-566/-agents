#!/usr/bin/env python3
"""
test_runner.py - Automated Test Runner and QA Verification for /swarm.
Auto-detects project test framework, executes suites, checks zero-emoji compliance,
and routes failures to gemini-coder via the swarm message bus.
Zero-Emoji Policy Enforced.
"""

import argparse
import datetime
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

EMOJI_REGEX = re.compile(
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


def detect_test_runner(cwd: Path) -> Optional[Tuple[str, List[str]]]:
    """Detects available test runner based on workspace files."""
    # Rust
    if (cwd / "Cargo.toml").exists():
        return ("cargo", ["cargo", "test"])

    # Go
    if (cwd / "go.mod").exists():
        return ("go", ["go", "test", "./..."])

    # Node / NPM
    if (cwd / "package.json").exists():
        try:
            with open(cwd / "package.json", "r", encoding="utf-8") as f:
                pkg = json.load(f)
            scripts = pkg.get("scripts", {})
            if "test" in scripts:
                return ("npm", ["npm", "test"])
        except Exception:
            pass

    # Python
    if (cwd / "pyproject.toml").exists() or (cwd / "pytest.ini").exists() or (cwd / "setup.py").exists():
        return ("pytest", [sys.executable, "-m", "pytest"])

    # Default fallback Python tests directory
    if (cwd / "tests").is_dir() or (cwd / "test").is_dir():
        return ("python-unittest", [sys.executable, "-m", "unittest", "discover", "-s", "tests" if (cwd / "tests").is_dir() else "test"])

    return None


def check_emojis_in_text(text: str) -> List[Tuple[int, str]]:
    violations = []
    lines = text.splitlines()
    for idx, line in enumerate(lines, start=1):
        matches = EMOJI_REGEX.findall(line)
        if matches:
            violations.append((idx, f"Found emojis {matches} on line {idx}"))
    return violations


def run_tests(
    cmd: List[str],
    cwd: Path,
    timeout: int = 120
) -> Dict[str, Any]:
    start_time = time.time()
    try:
        proc = subprocess.run(
            cmd,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout
        )
        elapsed = round(time.time() - start_time, 2)
        stdout = proc.stdout
        stderr = proc.stderr
        exit_code = proc.returncode
    except subprocess.TimeoutExpired as err:
        elapsed = round(time.time() - start_time, 2)
        stdout = err.stdout or "" if hasattr(err, "stdout") else ""
        stderr = (err.stderr or "") + f"\nTest timed out after {timeout} seconds."
        exit_code = 124
    except Exception as exc:
        elapsed = round(time.time() - start_time, 2)
        stdout = ""
        stderr = f"Failed to execute test runner: {exc}"
        exit_code = 1

    combined_output = f"{stdout}\n{stderr}"
    emoji_violations = check_emojis_in_text(combined_output)

    passed = (exit_code == 0) and (len(emoji_violations) == 0)

    return {
        "command": cmd,
        "exit_code": exit_code,
        "passed": passed,
        "elapsed_seconds": elapsed,
        "stdout": stdout,
        "stderr": stderr,
        "emoji_violations": emoji_violations,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }


def notify_bus_on_failure(
    swarm_dir: Path,
    report: Dict[str, Any],
    sender: str = "gemini-tester",
    recipient: str = "gemini-coder"
) -> None:
    try:
        from swarm_bus import send_message, update_task
    except ImportError:
        # Load relatively if running directly from scripts
        sys.path.insert(0, str(Path(__file__).parent))
        from swarm_bus import send_message, update_task

    subject = f"Test Failure Diagnostic: Command '{' '.join(report['command'])}' exited {report['exit_code']}"
    body = (
        f"QA Test Run Failed (Duration: {report['elapsed_seconds']}s)\n"
        f"Exit Code: {report['exit_code']}\n\n"
        f"--- STDERR ---\n{report['stderr'][-1500:]}\n\n"
        f"--- STDOUT ---\n{report['stdout'][-1500:]}\n"
    )
    if report["emoji_violations"]:
        body += f"\nZero-Emoji Violations Detected ({len(report['emoji_violations'])} instances):\n"
        for _, err in report["emoji_violations"][:5]:
            body += f"  - {err}\n"

    send_message(
        swarm_root=swarm_dir,
        sender=sender,
        recipient=recipient,
        subject=subject,
        body=body,
        msg_type="blocker",
        metadata={"exit_code": report["exit_code"], "elapsed": report["elapsed_seconds"]}
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Swarm Test Runner: Automated QA execution and bug feedback routing."
    )
    parser.add_argument("--cmd", help="Custom test command to execute")
    parser.add_argument("--cwd", default=".", help="Working directory for test execution")
    parser.add_argument("--timeout", type=int, default=120, help="Execution timeout in seconds")
    parser.add_argument("--swarm-dir", default=".swarm", help="Path to .swarm directory")
    parser.add_argument("--notify-coder", action="store_true", help="Post failure message directly to gemini-coder via bus")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")

    args = parser.parse_args()
    cwd_path = Path(args.cwd).resolve()
    swarm_path = Path(args.swarm_dir).resolve()

    if args.cmd:
        runner_name = "custom"
        cmd = args.cmd.split()
    else:
        detected = detect_test_runner(cwd_path)
        if not detected:
            msg = f"No supported test framework detected in {cwd_path}. Use --cmd to specify test command."
            if args.json:
                print(json.dumps({"error": msg}))
            else:
                print(f"[ERROR] {msg}", file=sys.stderr)
            sys.exit(1)
        runner_name, cmd = detected

    if not args.json:
        print(f"[INFO] Executing test runner '{runner_name}': {' '.join(cmd)}")

    report = run_tests(cmd, cwd=cwd_path, timeout=args.timeout)

    if args.notify_coder and not report["passed"] and swarm_path.exists():
        notify_bus_on_failure(swarm_path, report)
        if not args.json:
            print("[INFO] Dispatched test failure diagnostic to gemini-coder on Swarm Bus.")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        status_label = "[PASSED]" if report["passed"] else "[FAILED]"
        print(f"\n{status_label} QA Test Suite Run Complete ({report['elapsed_seconds']}s)")
        print(f"Exit Code: {report['exit_code']}")
        if report["emoji_violations"]:
            print(f"[VIOLATION] Zero-Emoji rule broken: {len(report['emoji_violations'])} emojis detected.")
        if not report["passed"]:
            if report["stderr"]:
                print(f"\n--- STDERR ---\n{report['stderr']}")
            if report["stdout"]:
                print(f"\n--- STDOUT ---\n{report['stdout']}")
        sys.exit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()

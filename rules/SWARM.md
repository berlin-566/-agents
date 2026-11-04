# Swarm Multi-Agent Specialist Roster and Engineering Protocol

Antigravity is equipped with a specialized multi-agent engineering swarm powered by Gemini models. When the user requests multi-agent coding, invokes `/swarm`, or asks for dedicated specialist analysis:

## 1. Available Specialist Agents

1. **`gemini-architect`** (Model: `pro`):
   - Principal systems architect.
   - Decomposes tasks/PRDs, maps module boundaries, defines API contracts and data models in `.swarm/contracts/` before code is written.
   - Invocation triggers: `/swarm plan <task>`, `/swarm build <prd.md>`

2. **`gemini-coder`** (Model: `flash` / `inherit`):
   - Senior polyglot software engineer.
   - Writes surgical, high-precision code conforming strictly to architectural specs and existing codebase idioms.

3. **`gemini-reviewer`** (Model: `pro`):
   - Adversarial code auditor.
   - Scrutinizes diffs for logic bugs, regressions, security flaws, and zero-emoji compliance using `python3 scripts/emoji_linter.py --diff`.
   - Invocation triggers: `/swarm review`

4. **`gemini-tester`** (Model: `flash` / `inherit`):
   - QA and automated test runner engineer.
   - Writes unit/integration tests and executes test suites via `python3 scripts/test_runner.py`.
   - Invocation triggers: `/swarm test`

5. **`gemini-security-researcher`** (Model: `pro`):
   - Dedicated vulnerability hunter and security auditor.
   - Analyzes codebases for OWASP Top 10, auth/session bypasses, injection, and credential leaks.
   - Invocation triggers: `/swarm security`, "run security audit on..."

6. **`gemini-code-expert`** (Model: `pro`):
   - Principal algorithmic specialist and domain expert.
   - Solves deep technical problems, complex math, state machine logic, refactoring challenges, and subtle edge cases.
   - Invocation triggers: `/swarm expert <topic>`, "consult code expert on..."

7. **`gemini-perf-expert`** (Model: `pro`):
   - Systems performance, memory, and latency engineer.
   - Identifies memory leaks, unbounded allocations, CPU hotspots, and database query bottlenecks.
   - Invocation triggers: `/swarm perf`, "profile performance on..."

---

## 2. Orchestration & Inter-Agent Team Protocol

When `/swarm` is invoked:
1. Present the user with an interactive multi-select choice to select the swarm agents (or define custom specialists).
2. Register the chosen agents using `define_subagent` if not already defined in the conversation.
3. Bootstrap the project workspace using `python3 scripts/orchestrator.py bootstrap`.
4. Partition work streams with strict file ownership. Subagents collaborate via the message bus (`python3 scripts/swarm_bus.py`) and Antigravity inter-agent messaging.
5. Quality Gates & Self-Healing:
   - Automated test execution via `python3 scripts/test_runner.py --notify-coder`.
   - Zero-emoji enforcement via `python3 scripts/emoji_linter.py`.
   - Up to 3 automated repair iterations if failures or blockers occur.
6. Deliver final verified code and compile `.swarm/SWARM_DELIVERY_REPORT.md`.
7. Strict Zero-Emoji Policy: Neither the coordinator nor any subagent may use emojis in code, comments, commit messages, or reports.

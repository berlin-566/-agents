# PRD Multi-Agent Team Orchestration Reference Guide

This reference provides concrete patterns for orchestrating an entire end-to-end engineering project using `/swarm`, establishing clean file boundaries, utilizing the inter-agent message bus, and coordinating peer collaboration across Gemini specialist models.

---

## 1. Project Directory Structure (`.swarm/`)

When a swarm project is initialized, the orchestrator sets up a structured project directory in the root of the workspace:

```text
.swarm/
├── team.json                # Registered agent roster with models and status
├── tasks.json               # Task state machine (PENDING, IN_PROGRESS, REVIEW, PASSED, BLOCKED, DONE)
├── bus.jsonl                # Append-only global inter-agent communication log
├── messages/                # Individual inbox directories per agent
│   ├── gemini-architect/
│   ├── gemini-coder/
│   ├── gemini-reviewer/
│   └── gemini-tester/
├── contracts/               # Shared API specs, data schemas, TypeScript/Python interface definitions
├── reports/                 # QA test outputs, security vulnerability scans, performance profiles
└── SWARM_DELIVERY_REPORT.md # Final signed-off engineering delivery report
```

---

## 2. Six-Phase Engineering Lifecycle

```text
Phase 1: INGESTION & RFC SPECIFICATION
  - gemini-architect ingests PRD or task description.
  - Inspects workspace layout and idioms.
  - Publishes interface contracts to `.swarm/contracts/`.
  - Dispatches tasks to task board: `python3 scripts/swarm_bus.py task create ...`
  - Broadcasts project kickoff: `python3 scripts/swarm_bus.py msg broadcast ...`

Phase 2: CONTRACT LOCK & TEST-DRIVEN SCAFFOLD
  - gemini-tester reviews `.swarm/contracts/` and drafts test suites under `tests/`.
  - Defines failing tests asserting requirements before code is written (TDD).
  - gemini-architect locks contract definitions.

Phase 3: COLLABORATIVE IMPLEMENTATION
  - gemini-coder picks up assigned tasks: `python3 scripts/swarm_bus.py task update --id <T> --status IN_PROGRESS`.
  - For complex algorithms or math, gemini-code-expert collaborates or implements core logic.
  - Strict file ownership enforced: each agent only edits files within their declared ownership boundary.

Phase 4: QUALITY GATES & VERIFICATION
  - gemini-tester runs automated test runner: `python3 scripts/test_runner.py`.
  - gemini-reviewer audits git diff for logic flaws, regressions, and runs `python3 scripts/emoji_linter.py --diff`.
  - gemini-security-researcher scans for OWASP vulnerabilities and credential leaks.
  - gemini-perf-expert profiles resource utilization and latency.

Phase 5: AUTOMATED SELF-HEALING LOOP
  - If tests fail or blockers are logged, diagnostics are automatically routed to gemini-coder via the swarm message bus.
  - gemini-coder applies surgical fixes.
  - Re-testing and re-auditing occur (up to 3 automated recovery cycles).

Phase 6: DELIVERY & SIGN-OFF
  - Orchestrator generates `.swarm/SWARM_DELIVERY_REPORT.md`.
  - Git commit finalized with descriptive conventional message.
```

---

## 3. Work-Stream Partitioning & Strict File Ownership

To avoid merge conflicts, each agent must have clearly partitioned file boundaries:

| Work Stream | Primary Owner | Secondary Reviewer | Declared File Ownership Scope |
| :--- | :--- | :--- | :--- |
| **API & Contracts** | `gemini-architect` | `gemini-coder` | `.swarm/contracts/*`, `src/types/*` |
| **Core Logic / Algorithmic**| `gemini-code-expert` | `gemini-reviewer` | `src/core/*`, `src/algorithms/*` |
| **Implementation / Integration** | `gemini-coder` | `gemini-reviewer` | `src/*` (excluding contracts/algorithms) |
| **QA & Automated Testing** | `gemini-tester` | `gemini-coder` | `tests/*`, `scripts/*` |
| **Security Audit** | `gemini-security-researcher` | `gemini-architect` | Read-only audit across all files |
| **Performance Profiling** | `gemini-perf-expert` | `gemini-coder` | Read-only profiling and benchmark scripts |

---

## 4. Inter-Agent Communication Examples

### Example 1: Architect Hands Off Contracts to Coder
```bash
python3 scripts/swarm_bus.py msg send \
  --from gemini-architect \
  --to gemini-coder \
  --subject "API Contract Finalized for Auth Module" \
  --body "Contracts published at .swarm/contracts/auth.ts. Begin implementation on src/auth/." \
  --type handoff
```

### Example 2: Tester Routes Test Failure to Coder
```bash
python3 scripts/swarm_bus.py msg send \
  --from gemini-tester \
  --to gemini-coder \
  --subject "[BLOCKER] Test Failure in test_token_expiry" \
  --body "AssertionError: Token expiry 3600 expected, got 0 in src/auth/token.py:45." \
  --type blocker
```

### Example 3: Coder Notifies Reviewer and Tester
```bash
python3 scripts/swarm_bus.py msg send \
  --from gemini-coder \
  --to gemini-reviewer \
  --subject "Fix Applied for test_token_expiry" \
  --body "Corrected default expiry calculation in src/auth/token.py:45. Ready for re-review." \
  --type handoff
```

### Example 4: Reviewer Approves Changes
```bash
python3 scripts/swarm_bus.py msg send \
  --from gemini-reviewer \
  --to coordinator \
  --subject "Review Clearance: Auth Module" \
  --body "Diff verified clean. Zero emojis present. All blockers resolved. APPROVED." \
  --type approval
```

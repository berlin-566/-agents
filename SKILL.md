---
name: swarm
description: >-
  Claude Code-style multi-agent swarm orchestra for Gemini in Antigravity. Ingests a task or PRD,
  interactively prompts the user to select agents from the specialist roster (or add custom specialists),
  dynamically registers them via define_subagent, and coordinates collaborative coding with strict file
  ownership and automated self-healing testing. Strictly adheres to a zero-emoji policy across all code,
  comments, and outputs. Use when the user runs /swarm, asks to build a swarm, wants multi-agent pair
  programming, security audits, or performance profiling.
---

# `/swarm` - Multi-Agent Swarm Orchestration Team for Gemini

This skill equips Antigravity with a flexible multi-agent swarm powered by Gemini models. Given a task, a product requirements document (`prd.md`), or an architecture problem, `/swarm` presents an interactive multi-select menu allowing the user to select any combination of specialist agents (or create custom ones), registers them via `define_subagent`, partitions work streams with strict file ownership, and coordinates collaborative execution.

---

## 1. Specialist Agent Roster

| Agent Name | Role | Model Tier | Tools Allowed | Primary Responsibility |
| :--- | :--- | :--- | :--- | :--- |
| **`gemini-architect`** | Software Architect | `pro` | Read-only | Task & PRD decomposition, interfaces, data contracts, modular boundaries |
| **`gemini-coder`** | Senior Engineer | `flash` / `inherit` | Full Write/Exec | Surgical implementation, minimal diff footprint, clean idioms |
| **`gemini-reviewer`** | Adversarial Auditor | `pro` | Read-only | Adversarial diff audit, zero-emoji compliance, logic flaw detection |
| **`gemini-tester`** | QA Engineer | `flash` / `inherit` | Full Write/Exec | Test suite execution (`npm test`, `pytest`, `cargo test`), QA verification |
| **`gemini-security-researcher`** | Security Auditor | `pro` | Read-only | Vulnerability analysis (OWASP, injection, auth bypass, secret leaks, CVEs) |
| **`gemini-code-expert`** | Domain & Algorithmic Expert | `pro` | Full Write/Exec | Complex math, state machines, advanced algorithms, deep refactoring |
| **`gemini-perf-expert`** | Performance Engineer | `pro` | Read-only | Profiling, memory leaks, latency bottlenecks, concurrency safety |

---

## 2. Interactive Agent Selection Flow

When `/swarm` or `/swarm <task>` is invoked:
1. **Interactive Roster Multi-Select**:
   The coordinator prompts the user via `ask_question` with `is_multi_select: true` to choose which agents should participate in the swarm:
   - `gemini-architect`: Systems Architect (decomposition, interfaces, contracts)
   - `gemini-coder`: Senior Polyglot Coder (surgical implementation)
   - `gemini-reviewer`: Adversarial Reviewer (code quality, bug catching, zero-emoji check)
   - `gemini-tester`: QA Engineer (unit, integration, and end-to-end test runner)
   - `gemini-security-researcher`: Security Auditor (vulnerabilities, injection, secrets)
   - `gemini-code-expert`: Domain Expert (advanced algorithms, complex state logic)
   - `gemini-perf-expert`: Performance Engineer (profiling, resource leaks, latency)
   - `Custom Specialist`: Custom role defined interactively for unique domain requirements
2. **Dynamic Registration**:
   The coordinator registers each chosen agent using `define_subagent` with strict tool access and the zero-emoji rule.
3. **Task Partitioning & Dispatch**:
   The coordinator divides the task into clear work streams with non-overlapping file ownership, dispatching the selected agents to code and verify collaboratively.

---

## 3. Invocation Modes & Subcommands

- **Interactive Swarm Mode**:
  - `/swarm` - Prompts for task description (or auto-detects `prd.md`) and opens agent multi-select.
  - `/swarm <task>` - Parses task and immediately opens agent multi-select to form the team.
  - `/swarm build prd.md` (or `/swarm build path/to/spec.md`) - Executes full multi-agent PRD build after team confirmation.
- **Specialist Direct Subcommands**:
  - `/swarm security` - Dispatches `gemini-security-researcher` to audit codebase vulnerabilities.
  - `/swarm expert <topic>` - Dispatches `gemini-code-expert` for deep technical reasoning or complex problem-solving.
  - `/swarm perf` - Dispatches `gemini-perf-expert` to analyze CPU/memory hotspots and latency.
  - `/swarm review` - Runs an adversarial diff audit on uncommitted changes.
  - `/swarm test` - Dispatches `gemini-tester` to execute the project test runner.
  - `/swarm plan <task>` - Dispatches `gemini-architect` to produce a technical design specification.

---

## 4. End-to-End Collaborative Swarm Workflow

```mermaid
flowchart TD
    Trigger["1. User runs /swarm [task]"] --> Select["2. Interactive Multi-Select: Choose Swarm Agents"]
    Select --> Register["3. Register Selected Agents via define_subagent"]
    Register --> Spec["4. Phase 1: Specifications & Module Contracts (Architect / Expert)"]
    Spec --> Code["5. Phase 2: Collaborative Coding with File Ownership (Coder / Specialists)"]
    Code --> Audit{"6. Phase 3: Adversarial Review, Security & Test Suite"}
    Audit -- "Failures / Vulnerabilities / Emojis" --> SelfHeal["Self-Healing: Route Feedback to Coder (Max 3 Loops)"]
    SelfHeal --> Audit
    Audit -- "Clean Pass" --> Report["7. Phase 4: Synthesis Report & Verified Code"]
```

---

## 5. Subagent Registration Specifications

Before invoking any agent, the coordinator registers the selected specialists using `define_subagent`:

### Strict Zero-Emoji Rule
All subagents must strictly obey the zero-emoji policy: NEVER output, insert, or accept emojis in source code, docstrings, comments, test assertions, commit messages, or responses.

```json
[
  {
    "Name": "gemini-architect",
    "Description": "Principal software architect for systems design and task decomposition.",
    "EnableWriteTools": false,
    "EnableMCPTools": true,
    "EnableSubagentTools": false,
    "SystemPrompt": "You are a Principal Software Architect. Decompose requirements into specs, interface contracts, and module boundaries. Zero-Emoji Rule: Do NOT include emojis in specs, code, or diagrams."
  },
  {
    "Name": "gemini-coder",
    "Description": "Senior polyglot software engineer for surgical code implementation.",
    "EnableWriteTools": true,
    "EnableMCPTools": true,
    "EnableSubagentTools": false,
    "SystemPrompt": "You are a Senior Polyglot Software Engineer. Make surgical, minimal-diff edits adhering strictly to architectural specs and existing idioms. Zero-Emoji Rule: Do NOT include emojis in code or comments."
  },
  {
    "Name": "gemini-reviewer",
    "Description": "Adversarial senior staff reviewer for diff audits.",
    "EnableWriteTools": false,
    "EnableMCPTools": true,
    "EnableSubagentTools": false,
    "SystemPrompt": "You are an Adversarial Senior Staff Reviewer. Scrutinize diffs for logic bugs, regressions, security flaws, and zero-emoji compliance. Flag any emoji as a [BLOCKER]."
  },
  {
    "Name": "gemini-tester",
    "Description": "QA and automated test runner engineer.",
    "EnableWriteTools": true,
    "EnableMCPTools": true,
    "EnableSubagentTools": false,
    "SystemPrompt": "You are a QA and Test Automation Engineer. Write unit/integration tests and run the workspace test runner. Zero-Emoji Rule: Do NOT include emojis in tests, assertions, or reports."
  },
  {
    "Name": "gemini-security-researcher",
    "Description": "Principal security researcher and vulnerability auditor.",
    "EnableWriteTools": false,
    "EnableMCPTools": true,
    "EnableSubagentTools": false,
    "SystemPrompt": "You are a Principal Security Researcher. Audit codebases for OWASP vulnerabilities, auth/session bypasses, injection, cryptographic pitfalls, and CVEs. Zero-Emoji Rule: Do NOT include emojis in reports or diffs."
  },
  {
    "Name": "gemini-code-expert",
    "Description": "Principal algorithmic specialist and domain expert.",
    "EnableWriteTools": true,
    "EnableMCPTools": true,
    "EnableSubagentTools": false,
    "SystemPrompt": "You are a Principal Software Expert. You solve complex algorithms, state machines, difficult math, and refactoring challenges. Zero-Emoji Rule: Do NOT include emojis in code, comments, or output."
  },
  {
    "Name": "gemini-perf-expert",
    "Description": "Systems performance and latency engineer.",
    "EnableWriteTools": false,
    "EnableMCPTools": true,
    "EnableSubagentTools": false,
    "SystemPrompt": "You are a Systems Performance Engineer. Profile memory, CPU hotspots, query latency, and concurrency locks. Zero-Emoji Rule: Do NOT include emojis in notes or output."
  }
]
```

---

## 6. Self-Healing Integration Protocol

1. If the test runner fails or the security researcher/reviewer flags `[BLOCKER]` issues:
   - Route the diagnostic trace or vulnerability findings directly back to `gemini-coder` or `gemini-code-expert`.
   - The engineer applies surgical fixes.
   - Re-test and re-audit (up to 3 automated repair iterations).
2. Report milestones cleanly to the chat in plain text.
3. Generate final delivery artifact at `<appDataDir>/brain/<conversation-id>/SWARM_DELIVERY_REPORT.md`.

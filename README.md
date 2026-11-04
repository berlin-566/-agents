# `/swarm`

> **Claude Code-style multi-agent swarm orchestration for Gemini in Google Antigravity.**  
> Ingests a task or `prd.md`, interactively prompts for agent selection, dynamically registers specialized engineer agents, partitions work streams, codes collaboratively, and verifies everything with an automated self-healing test loop.

[![Antigravity Skill](https://img.shields.io/badge/Antigravity-Skill-blue?style=flat-square)](https://github.com/berlin-566/-swarm)
[![Gemini Models](https://img.shields.io/badge/Gemini-3.8_Pro_%26_Flash-orange?style=flat-square)](https://deepmind.google/technologies/gemini/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

---

## Quick Install (One-Liner)

Install the complete swarm suite with a single command:

```bash
curl -fsSL https://raw.githubusercontent.com/berlin-566/-swarm/main/install.sh | bash
```

### What the Auto-Installer Handles
- **Multi-Agent Plugin & Rules Registration**: Automatically installs both the `/swarm` skill and the Antigravity plugin rules (`plugins/swarm/rules/SWARM.md`) so that Antigravity automatically knows and registers all specialist agents out-of-the-box in every session.
- **Directory Detection & Creation**: Automatically checks if `~/.gemini/config/skills/swarm` and `~/.gemini/config/plugins/swarm` exist, creating missing directories automatically.
- **Legacy Cleanup**: Automatically cleans up legacy `agents` plugin and skill folders to avoid any clashes.
- **Smart Upgrades**: Cleanly updates existing installations to the latest release.
- **Integrity Validation**: Verifies file sizes and integrity after downloading.
- **Zero Configuration**: Ready to use immediately across all your Antigravity workspaces.

### Optional: Local Workspace Install
To install only into the current project repository (`.swarm/`):

```bash
curl -fsSL https://raw.githubusercontent.com/berlin-566/-swarm/main/install.sh | bash -s -- --local
```

---

## The Specialist Agent Roster

Antigravity equips your workspace with seven dedicated specialist agents tailored to Gemini model tiers:

| Agent | Role | Model | Focus Area |
| :--- | :--- | :--- | :--- |
| **`gemini-architect`** | Systems Architect | `pro` | Task/PRD decomposition, interface definitions, API contracts, modular bounds |
| **`gemini-coder`** | Senior Engineer | `flash` | Surgical code implementation, minimal diff footprint, language idioms |
| **`gemini-reviewer`** | Adversarial Auditor | `pro` | Adversarial diff audit, regression catch, zero-emoji compliance |
| **`gemini-tester`** | QA Engineer | `flash` | Automated test suite execution (`npm test`, `pytest`, `cargo test`), test generation |
| **`gemini-security-researcher`** | Security Auditor | `pro` | OWASP Top 10, auth/session bypass, injection, secret leaks, CVE analysis |
| **`gemini-code-expert`** | Algorithmic Specialist | `pro` | Deep math, state machines, difficult algorithms, architectural refactoring |
| **`gemini-perf-expert`** | Performance Engineer | `pro` | CPU/memory profiling, leak detection, latency bottlenecks, concurrency |

---

## Mental Model & Swarm Workflow

```mermaid
flowchart TD
    Trigger["1. User invokes /swarm [task or prd]"] --> Select["2. Interactive Multi-Select: Choose Swarm Agents"]
    Select --> Register["3. Register Chosen Agents via define_subagent"]
    Register --> Spec["4. Phase 1: Foundations & Type Contracts (Architect / Expert)"]
    Spec --> Code["5. Phase 2: Collaborative Team Coding (Coder / Specialists)"]
    Code --> Audit{"6. Phase 3: Adversarial Review, Security & Test Suite"}
    Audit -- "Issues / Failures / Emojis" --> Repair["Self-Healing: Route Tracebacks to Coder (Max 3 Loops)"]
    Repair --> Audit
    Audit -- "Clean Pass" --> Done["7. Phase 4: Delivery Report & Verified Code"]
```

---

## Key Features

- **Interactive Swarm Selection**: Whenever you run `/swarm` or `/swarm <task>`, you are presented with an interactive multi-select menu to choose exactly which agents to deploy, including custom specialist roles.
- **Collaborative Orchestration**: Selected agents are dynamically registered via `define_subagent` and coordinated like subagents working together with clean module handoffs.
- **Strict Zero-Emoji Policy**: Agents are strictly instructed never to insert or generate emojis in source code, docstrings, comments, test suites, commit messages, or chat updates. Reviewers automatically flag any emoji as a blocker.
- **Smart Model Tiering**: High-reasoning `pro` models handle architecture, security audits, and adversarial reviews; high-speed `flash`/`inherit` models handle code editing and test loops.
- **Strict File Ownership**: Agents work with partitioned boundaries, preventing conflicting edits and diff collisions.
- **Automated Self-Healing Loop**: If tests fail or the reviewer/security auditor flags blockers, tracebacks and audit logs are immediately fed back to the responsible agent for automatic repair (up to 3 iterations).
- **In-Tree Workspace (`inherit`)**: All agents operate directly in your workspace with full access to project dependencies, environment variables, and git state.

---

## Usage & Subcommands

### 1. Interactive Swarm
Run `/swarm` or provide a task directly:

```bash
/swarm
/swarm build user authentication service with JWT and refresh tokens
/swarm build prd.md
```

Antigravity will prompt you to select the agents you want on your swarm team, dynamically register them, and begin collaborative execution.

### 2. Specialist Subcommands
You can also call any specialist individually on demand:

| Command | Action |
| :--- | :--- |
| `/swarm build prd.md` | Full multi-agent swarm build from PRD |
| `/swarm security` | Dispatches Security Researcher to audit vulnerabilities and CVEs |
| `/swarm expert <topic>` | Dispatches Code Expert for deep algorithmic or architectural problems |
| `/swarm perf` | Dispatches Performance Engineer to profile memory and CPU bottlenecks |
| `/swarm review` | Dispatches Adversarial Reviewer on current uncommitted `git diff` |
| `/swarm test` | Dispatches QA Engineer to write tests and run project test runner |
| `/swarm plan <task>` | Dispatches Architect to generate technical spec & contracts |

---

## Repository Structure

```text
-swarm/
|-- SKILL.md                          # Antigravity skill manifest & orchestration rules
|-- plugin.json                       # Antigravity plugin manifest
|-- rules/
|   `-- SWARM.md                      # Always-active rule registering the expanded specialist roster
|-- install.sh                        # Auto-installer for skills and plugin rules
|-- uninstall.sh                      # Clean removal script
|-- references/
|   |-- agent_prompts.md              # System prompts for all 7 specialist agents
|   `-- team_orchestration.md         # PRD decomposition & file isolation guidelines
|-- README.md                         # Documentation & quickstart
`-- LICENSE                           # MIT License
```

---

## Manual Installation

If you prefer not to use `curl`, clone the repository and run the local installer:

```bash
git clone https://github.com/berlin-566/-swarm.git /tmp/-swarm
/tmp/-swarm/install.sh
rm -rf /tmp/-swarm
```

---

## License

Released under the [MIT License](LICENSE).

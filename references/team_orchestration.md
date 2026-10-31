# PRD Multi-Agent Team Orchestration Reference Guide

This reference provides concrete patterns for decomposing a PRD into modular work streams, establishing clean file ownership boundaries, and conducting multi-agent team coding in Antigravity.

---

## 1. PRD Work-Stream Decomposition Pattern

When given a `prd.md`, the coordinator should break the specification into a Dependency Matrix:

| Stream | Responsible Agent | Upstream Dependencies | Output Artifacts / Files |
| :--- | :--- | :--- | :--- |
| **0. Foundations** | `db-architect` / `lead-architect` | PRD Requirements | Database schemas, type definitions, shared interfaces (`src/types/*`) |
| **1. Data Layer** | `db-architect` | Schemas & Migrations | ORM models, migration scripts, repository queries (`src/db/*`) |
| **2. Core Services & API**| `backend-engineer` | Shared Types + Data Layer | Controllers, routes, services, middleware (`src/api/*`, `src/services/*`) |
| **3. UI & Client State** | `frontend-engineer` | Shared Types + API Spec | Views, components, API client hooks, UI state (`src/ui/*`, `src/components/*`) |
| **4. Integration & Entry**| Coordinator / Lead | Backend + Frontend | Router mounting, app initialization, env loading (`src/main.ts`, `src/app.ts`) |
| **5. QA & Diff Audit** | `qa-auditor` | Integrated App | Unit/integration test suites (`tests/*`), verification runs, diff security check |

---

## 2. Dynamic Team Generation Templates

### Template A: Fullstack Web / Mobile App
```json
[
  {
    "Name": "db-architect",
    "Description": "Database and data layer specialist.",
    "EnableWriteTools": true,
    "EnableMCPTools": true,
    "EnableSubagentTools": false,
    "SystemPrompt": "You are a Database Specialist and Systems Architect. Your job is to define schema migrations, ORM entities, and database queries adhering to the PRD. Ensure relational integrity, proper indexing, and clean type exports."
  },
  {
    "Name": "backend-engineer",
    "Description": "Backend and API specialist.",
    "EnableWriteTools": true,
    "EnableMCPTools": true,
    "EnableSubagentTools": false,
    "SystemPrompt": "You are a Senior Backend Engineer. Your job is to implement server routes, controllers, and services using the shared type definitions and database queries. Write robust error handling, validation, and clean REST/RPC endpoints."
  },
  {
    "Name": "frontend-engineer",
    "Description": "Frontend UI and state specialist.",
    "EnableWriteTools": true,
    "EnableMCPTools": true,
    "EnableSubagentTools": false,
    "SystemPrompt": "You are a Senior Frontend Engineer. Your job is to build user interfaces, components, and state management hooks based on the PRD. Integrate seamlessly with the defined backend endpoints. Focus on responsive, clean, and accessible UI."
  },
  {
    "Name": "qa-auditor",
    "Description": "QA, automated testing, and security auditor.",
    "EnableWriteTools": true,
    "EnableMCPTools": true,
    "EnableSubagentTools": false,
    "SystemPrompt": "You are a Staff QA Engineer and Adversarial Auditor. Your job is to verify that all PRD requirements are met. Scrutinize the git diff for bugs or security flaws, write automated test cases, and execute the test runner to prove everything passes."
  }
]
```

### Template B: Systems / CLI Tool / Backend Service
```json
[
  {
    "Name": "engine-architect",
    "Description": "Core domain logic and data structures engineer.",
    "EnableWriteTools": true,
    "EnableMCPTools": true,
    "EnableSubagentTools": false,
    "SystemPrompt": "You are a Systems Architect. You design and implement the core engine, data structures, and algorithms required by the PRD. Emphasize performance, memory safety, and modularity."
  },
  {
    "Name": "cli-engineer",
    "Description": "Command-line interface and I/O engineer.",
    "EnableWriteTools": true,
    "EnableMCPTools": true,
    "EnableSubagentTools": false,
    "SystemPrompt": "You are a CLI/UX Engineer. You implement the argument parser, terminal output formatting, configuration loader, and shell interactions, wiring them into the core engine."
  },
  {
    "Name": "qa-auditor",
    "Description": "Test automation and regression specialist.",
    "EnableWriteTools": true,
    "EnableMCPTools": true,
    "EnableSubagentTools": false,
    "SystemPrompt": "You are a QA and Test Automation Engineer. You write comprehensive unit and integration tests, verify CLI flags and error exits, and run test suites to guarantee zero regressions."
  }
]
```

---

## 3. Collaborative Handoff Protocol

To ensure subagents work together seamlessly without merge conflicts:
1. **Contract Handoff**: The output of the Foundations phase (e.g. `src/types/index.ts`) must be shared in the prompt of subsequent engineering agents.
2. **File Isolation**: When dispatching `backend-engineer`, explicitly state: *"You own files under `src/api/` and `src/services/`. Do not edit files under `src/ui/`."*
3. **Cross-Agent Fixes**: If a frontend agent reports an incompatible response schema from the backend, the coordinator routes an adjustment request back to `backend-engineer` rather than letting the frontend agent rewrite backend code.

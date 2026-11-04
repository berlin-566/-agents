"""
verification_engine.py - Autonomous Engine Verification Logic for /swarm.
Provides workspace integrity checks, deterministic state machine transitions,
and diagnostic dispatching.
Zero-Emoji Policy Enforced.
"""

import datetime
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Ensure scripts directory is available for swarm_bus import
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

try:
    import swarm_bus
except ImportError:
    swarm_bus = None


def iso_now() -> str:
    """Return current UTC timestamp in ISO-8601 format."""
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


VALID_STATUSES = ["PENDING", "IN_PROGRESS", "REVIEW", "PASSED", "BLOCKED", "DONE"]

VALID_TRANSITIONS: Dict[str, List[str]] = {
    "PENDING": ["IN_PROGRESS"],
    "IN_PROGRESS": ["REVIEW"],
    "REVIEW": ["PASSED", "BLOCKED"],
    "BLOCKED": ["REVIEW"],
    "PASSED": ["DONE"],
    "DONE": [],
}


class VerificationEngine:
    """Core verification and state transition engine for Swarm autonomous agents."""

    def __init__(self, swarm_root: Path) -> None:
        """Initialize engine bound to active .swarm workspace."""
        self.swarm_root = Path(swarm_root)
        # If the path points to a project containing .swarm and not team.json directly,
        # resolve to the .swarm sub-folder.
        if (self.swarm_root / ".swarm").is_dir() and not (self.swarm_root / "team.json").exists():
            self.swarm_root = self.swarm_root / ".swarm"

    def verify_workspace_integrity(self) -> Dict[str, Any]:
        """
        Validates presence and schema conformance of team.json, tasks.json,
        bus.jsonl, and subdirectories (messages, contracts, reports).
        Returns: { "valid": bool, "errors": List[str] }
        """
        errors: List[str] = []

        if not self.swarm_root.exists():
            return {
                "valid": False,
                "errors": [f"Swarm root directory does not exist: {self.swarm_root}"]
            }

        if not self.swarm_root.is_dir():
            return {
                "valid": False,
                "errors": [f"Swarm root path is not a directory: {self.swarm_root}"]
            }

        # Check required subdirectories
        required_dirs = ["messages", "contracts", "reports"]
        for dirname in required_dirs:
            target_dir = self.swarm_root / dirname
            if not target_dir.exists():
                errors.append(f"Missing required directory: {dirname}")
            elif not target_dir.is_dir():
                errors.append(f"Path is not a directory: {dirname}")

        # Check required files
        required_files = ["team.json", "tasks.json", "bus.jsonl"]
        for filename in required_files:
            target_file = self.swarm_root / filename
            if not target_file.exists():
                errors.append(f"Missing required file: {filename}")
            elif not target_file.is_file():
                errors.append(f"Path is not a file: {filename}")

        # Validate team.json schema if present
        team_file = self.swarm_root / "team.json"
        if team_file.is_file():
            try:
                with open(team_file, "r", encoding="utf-8") as f:
                    team_data = json.load(f)
                if not isinstance(team_data, dict):
                    errors.append("team.json must be a JSON object")
                elif "agents" not in team_data or not isinstance(team_data["agents"], dict):
                    errors.append("team.json missing 'agents' object")
            except Exception as exc:
                errors.append(f"team.json failed JSON decoding: {exc}")

        # Validate tasks.json schema if present
        tasks_file = self.swarm_root / "tasks.json"
        if tasks_file.is_file():
            try:
                with open(tasks_file, "r", encoding="utf-8") as f:
                    tasks_data = json.load(f)
                if not isinstance(tasks_data, dict):
                    errors.append("tasks.json must be a JSON object")
                elif "tasks" not in tasks_data or not isinstance(tasks_data["tasks"], list):
                    errors.append("tasks.json missing 'tasks' array")
                else:
                    required_task_fields = ["id", "title", "assignee", "status"]
                    for idx, t in enumerate(tasks_data["tasks"]):
                        if not isinstance(t, dict):
                            errors.append(f"Task at index {idx} in tasks.json is not an object")
                            continue
                        for req_f in required_task_fields:
                            if req_f not in t:
                                errors.append(f"Task '{t.get('id', idx)}' missing required field: {req_f}")
            except Exception as exc:
                errors.append(f"tasks.json failed JSON decoding: {exc}")

        # Validate bus.jsonl lines if present
        bus_file = self.swarm_root / "bus.jsonl"
        if bus_file.is_file():
            try:
                with open(bus_file, "r", encoding="utf-8") as f:
                    for line_no, line in enumerate(f, start=1):
                        stripped = line.strip()
                        if not stripped:
                            continue
                        try:
                            msg = json.loads(stripped)
                            if not isinstance(msg, dict):
                                errors.append(f"bus.jsonl line {line_no} is not a JSON object")
                        except Exception as exc:
                            errors.append(f"bus.jsonl line {line_no} invalid JSON: {exc}")
            except Exception as exc:
                errors.append(f"bus.jsonl read error: {exc}")

        return {
            "valid": len(errors) == 0,
            "errors": errors
        }

    def execute_state_transition(
        self,
        task_id: str,
        target_status: str,
        actor: str,
        note: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Performs validated state machine transition.
        Raises ValueError if transition is invalid or preconditions unmet.
        Returns updated task dict.
        """
        target_status_upper = target_status.upper()
        if target_status_upper not in VALID_STATUSES:
            raise ValueError(
                f"Unknown target status '{target_status}'. Valid statuses: {VALID_STATUSES}"
            )

        tasks_file = self.swarm_root / "tasks.json"
        if not tasks_file.exists():
            raise ValueError(f"tasks.json not found in workspace: {self.swarm_root}")

        try:
            with open(tasks_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as exc:
            raise ValueError(f"Failed to read tasks.json: {exc}")

        tasks = data.get("tasks", [])
        target_task = None
        for t in tasks:
            if t.get("id") == task_id:
                target_task = t
                break

        if target_task is None:
            raise ValueError(f"Task with ID '{task_id}' not found.")

        current_status = target_task.get("status", "PENDING").upper()
        allowed_transitions = VALID_TRANSITIONS.get(current_status, [])

        if target_status_upper not in allowed_transitions:
            raise ValueError(
                f"Invalid state transition for task '{task_id}': "
                f"cannot transition from '{current_status}' to '{target_status_upper}'. "
                f"Allowed transitions: {allowed_transitions}"
            )

        timestamp = iso_now()
        target_task["status"] = target_status_upper
        target_task["updated_at"] = timestamp

        if "notes" not in target_task or not isinstance(target_task["notes"], list):
            target_task["notes"] = []

        audit_text = f"[{actor}] {note}" if note else f"[{actor}] Transitioned to {target_status_upper}"
        target_task["notes"].append({
            "timestamp": timestamp,
            "note": audit_text,
            "actor": actor
        })

        with open(tasks_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        return target_task

    def dispatch_diagnostic(
        self,
        recipient: str,
        subject: str,
        diagnostic_payload: Dict[str, Any],
        sender: str = "verification-engine"
    ) -> str:
        """
        Formats and dispatches blocker message onto swarm bus.
        Returns generated message ID.
        """
        if swarm_bus is None:
            raise RuntimeError("swarm_bus module could not be imported")

        effective_sender = sender
        if isinstance(diagnostic_payload, dict) and "sender" in diagnostic_payload:
            effective_sender = diagnostic_payload["sender"]

        body_str = json.dumps(diagnostic_payload, indent=2)
        msg_obj = swarm_bus.send_message(
            swarm_root=self.swarm_root,
            sender=effective_sender,
            recipient=recipient,
            subject=subject,
            body=body_str,
            msg_type="blocker",
            metadata=diagnostic_payload
        )
        return msg_obj["id"]

#!/usr/bin/env python3
"""
swarm_bus.py - Inter-Agent Message Bus and Project Coordinator for /swarm.
Provides communication, task tracking, and state management for Gemini multi-agent teams.
Zero-Emoji Policy Enforced.
"""

import argparse
import datetime
import json
import os
import sys
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

DEFAULT_SWARM_DIR = ".swarm"


def get_swarm_root(custom_path: Optional[str] = None) -> Path:
    if custom_path:
        return Path(custom_path)
    # Check environment variable or fallback to .swarm in current working directory
    env_path = os.getenv("SWARM_DIR")
    if env_path:
        return Path(env_path)
    return Path(DEFAULT_SWARM_DIR)


def ensure_initialized(swarm_root: Path) -> None:
    if not (swarm_root / "team.json").exists():
        init_workspace(swarm_root)


def init_workspace(swarm_root: Path, force: bool = False) -> None:
    if swarm_root.exists() and not force and (swarm_root / "team.json").exists():
        return

    swarm_root.mkdir(parents=True, exist_ok=True)
    (swarm_root / "messages").mkdir(parents=True, exist_ok=True)
    (swarm_root / "contracts").mkdir(parents=True, exist_ok=True)
    (swarm_root / "reports").mkdir(parents=True, exist_ok=True)

    if not (swarm_root / "team.json").exists() or force:
        with open(swarm_root / "team.json", "w", encoding="utf-8") as f:
            json.dump({"agents": {}, "created_at": iso_now()}, f, indent=2)

    if not (swarm_root / "tasks.json").exists() or force:
        with open(swarm_root / "tasks.json", "w", encoding="utf-8") as f:
            json.dump({"tasks": [], "phase": "INITIALIZATION", "created_at": iso_now()}, f, indent=2)

    if not (swarm_root / "bus.jsonl").exists() or force:
        with open(swarm_root / "bus.jsonl", "w", encoding="utf-8") as f:
            pass


def iso_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


# -----------------------------------------------------------------------------
# Team Management
# -----------------------------------------------------------------------------

def register_agent(
    swarm_root: Path,
    name: str,
    role: str,
    model: str = "inherit",
    conv_id: Optional[str] = None,
    status: str = "active"
) -> Dict[str, Any]:
    ensure_initialized(swarm_root)
    team_file = swarm_root / "team.json"
    with open(team_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    agent_entry = {
        "name": name,
        "role": role,
        "model": model,
        "conv_id": conv_id or "",
        "status": status,
        "registered_at": iso_now(),
        "last_seen": iso_now()
    }
    data["agents"][name] = agent_entry

    with open(team_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return agent_entry


def get_team(swarm_root: Path) -> Dict[str, Any]:
    ensure_initialized(swarm_root)
    team_file = swarm_root / "team.json"
    with open(team_file, "r", encoding="utf-8") as f:
        return json.load(f).get("agents", {})


# -----------------------------------------------------------------------------
# Messaging & Communication Bus
# -----------------------------------------------------------------------------

def send_message(
    swarm_root: Path,
    sender: str,
    recipient: str,
    subject: str,
    body: str,
    msg_type: str = "chat",
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    ensure_initialized(swarm_root)
    msg_id = f"msg_{int(datetime.datetime.now().timestamp() * 1000)}_{uuid.uuid4().hex[:6]}"
    timestamp = iso_now()

    msg_obj = {
        "id": msg_id,
        "from": sender,
        "to": recipient,
        "subject": subject,
        "body": body,
        "type": msg_type,
        "read": False,
        "timestamp": timestamp,
        "metadata": metadata or {}
    }

    # Append to global bus log
    with open(swarm_root / "bus.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(msg_obj) + "\n")

    # Store individual message file for fast recipient polling
    recipient_dir = swarm_root / "messages" / recipient
    recipient_dir.mkdir(parents=True, exist_ok=True)
    with open(recipient_dir / f"{msg_id}.json", "w", encoding="utf-8") as f:
        json.dump(msg_obj, f, indent=2)

    return msg_obj


def broadcast_message(
    swarm_root: Path,
    sender: str,
    subject: str,
    body: str,
    msg_type: str = "broadcast",
    metadata: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    ensure_initialized(swarm_root)
    team = get_team(swarm_root)
    recipients = [name for name in team.keys() if name != sender]
    if not recipients:
        # Default fallback recipients if team not pre-registered
        recipients = ["gemini-architect", "gemini-coder", "gemini-reviewer", "gemini-tester"]

    results = []
    for recipient in recipients:
        res = send_message(
            swarm_root=swarm_root,
            sender=sender,
            recipient=recipient,
            subject=subject,
            body=body,
            msg_type=msg_type,
            metadata=metadata
        )
        results.append(res)
    return results


def read_messages(
    swarm_root: Path,
    agent: str,
    unread_only: bool = False,
    mark_read: bool = True
) -> List[Dict[str, Any]]:
    ensure_initialized(swarm_root)
    agent_dir = swarm_root / "messages" / agent
    if not agent_dir.exists():
        return []

    messages = []
    for filepath in sorted(agent_dir.glob("*.json")):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            if unread_only and data.get("read", False):
                continue
            messages.append(data)
            if mark_read and not data.get("read", False):
                data["read"] = True
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
        except Exception:
            continue

    return messages


def get_bus_log(swarm_root: Path, limit: int = 50) -> List[Dict[str, Any]]:
    ensure_initialized(swarm_root)
    bus_file = swarm_root / "bus.jsonl"
    if not bus_file.exists():
        return []

    lines = []
    with open(bus_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    lines.append(json.loads(line))
                except Exception:
                    pass
    return lines[-limit:]


# -----------------------------------------------------------------------------
# Task Board & Project State
# -----------------------------------------------------------------------------

VALID_STATUSES = ["PENDING", "IN_PROGRESS", "REVIEW", "PASSED", "BLOCKED", "DONE"]


def create_task(
    swarm_root: Path,
    task_id: str,
    title: str,
    assignee: str,
    description: str = "",
    deps: Optional[List[str]] = None,
    files_owned: Optional[List[str]] = None
) -> Dict[str, Any]:
    ensure_initialized(swarm_root)
    tasks_file = swarm_root / "tasks.json"
    with open(tasks_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Check for duplicate
    for t in data["tasks"]:
        if t["id"] == task_id:
            raise ValueError(f"Task with ID '{task_id}' already exists.")

    task_obj = {
        "id": task_id,
        "title": title,
        "description": description,
        "assignee": assignee,
        "status": "PENDING",
        "deps": deps or [],
        "files_owned": files_owned or [],
        "notes": [],
        "created_at": iso_now(),
        "updated_at": iso_now()
    }
    data["tasks"].append(task_obj)

    with open(tasks_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return task_obj


def update_task(
    swarm_root: Path,
    task_id: str,
    status: Optional[str] = None,
    notes: Optional[str] = None,
    assignee: Optional[str] = None
) -> Dict[str, Any]:
    ensure_initialized(swarm_root)
    tasks_file = swarm_root / "tasks.json"
    with open(tasks_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    found = None
    for t in data["tasks"]:
        if t["id"] == task_id:
            found = t
            break

    if not found:
        raise KeyError(f"Task with ID '{task_id}' not found.")

    if status:
        if status.upper() not in VALID_STATUSES:
            raise ValueError(f"Invalid status '{status}'. Valid: {VALID_STATUSES}")
        found["status"] = status.upper()

    if assignee:
        found["assignee"] = assignee

    if notes:
        found["notes"].append({
            "timestamp": iso_now(),
            "note": notes
        })

    found["updated_at"] = iso_now()

    with open(tasks_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return found


def list_tasks(
    swarm_root: Path,
    status: Optional[str] = None,
    assignee: Optional[str] = None
) -> List[Dict[str, Any]]:
    ensure_initialized(swarm_root)
    tasks_file = swarm_root / "tasks.json"
    with open(tasks_file, "r", encoding="utf-8") as f:
        tasks = json.load(f).get("tasks", [])

    filtered = tasks
    if status:
        filtered = [t for t in filtered if t.get("status", "").upper() == status.upper()]
    if assignee:
        filtered = [t for t in filtered if t.get("assignee") == assignee]

    return filtered


def set_phase(swarm_root: Path, phase: str) -> str:
    ensure_initialized(swarm_root)
    tasks_file = swarm_root / "tasks.json"
    with open(tasks_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    data["phase"] = phase.upper()
    data["phase_updated_at"] = iso_now()
    with open(tasks_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return phase.upper()


def get_dashboard_status(swarm_root: Path) -> Dict[str, Any]:
    ensure_initialized(swarm_root)
    team = get_team(swarm_root)
    tasks_file = swarm_root / "tasks.json"
    with open(tasks_file, "r", encoding="utf-8") as f:
        task_data = json.load(f)

    tasks = task_data.get("tasks", [])
    phase = task_data.get("phase", "INITIALIZATION")

    # Count tasks by status
    status_counts = {s: 0 for s in VALID_STATUSES}
    for t in tasks:
        s = t.get("status", "PENDING")
        if s in status_counts:
            status_counts[s] += 1

    # Count unread messages per agent
    unread_counts = {}
    for agent in team.keys():
        msgs = read_messages(swarm_root, agent, unread_only=True, mark_read=False)
        unread_counts[agent] = len(msgs)

    return {
        "phase": phase,
        "team_size": len(team),
        "team": team,
        "task_counts": status_counts,
        "total_tasks": len(tasks),
        "tasks": tasks,
        "unread_messages": unread_counts
    }


# -----------------------------------------------------------------------------
# CLI Entrypoint
# -----------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Swarm Bus: Multi-agent communication and task tracking for /swarm."
    )
    parser.add_argument("--swarm-dir", default=None, help="Path to .swarm directory")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # init
    p_init = subparsers.add_parser("init", help="Initialize .swarm project workspace")
    p_init.add_argument("--force", action="store_true", help="Overwrite existing workspace state")

    # team
    p_team = subparsers.add_parser("team", help="Manage swarm team members")
    p_team_sub = p_team.add_subparsers(dest="subcommand", required=True)

    p_t_reg = p_team_sub.add_parser("register", help="Register an agent in the team")
    p_t_reg.add_argument("--name", required=True, help="Agent name")
    p_t_reg.add_argument("--role", required=True, help="Agent role description")
    p_t_reg.add_argument("--model", default="inherit", help="Model tier (pro, flash, inherit)")
    p_t_reg.add_argument("--conv-id", default=None, help="Conversation ID for subagent")

    p_team_sub.add_parser("list", help="List all registered agents")

    # msg
    p_msg = subparsers.add_parser("msg", help="Inter-agent communication commands")
    p_msg_sub = p_msg.add_subparsers(dest="subcommand", required=True)

    p_m_send = p_msg_sub.add_parser("send", help="Send a message to an agent")
    p_m_send.add_argument("--from", dest="sender", required=True, help="Sender agent name")
    p_m_send.add_argument("--to", dest="recipient", required=True, help="Recipient agent name")
    p_m_send.add_argument("--subject", required=True, help="Message subject")
    p_m_send.add_argument("--body", required=True, help="Message body content")
    p_m_send.add_argument("--type", default="chat", choices=["chat", "handoff", "blocker", "approval", "rfc", "review"], help="Message category")

    p_m_bcast = p_msg_sub.add_parser("broadcast", help="Broadcast message to all team members")
    p_m_bcast.add_argument("--from", dest="sender", required=True, help="Sender agent name")
    p_m_bcast.add_argument("--subject", required=True, help="Broadcast subject")
    p_m_bcast.add_argument("--body", required=True, help="Broadcast body content")
    p_m_bcast.add_argument("--type", default="broadcast", help="Message category")

    p_m_read = p_msg_sub.add_parser("read", help="Read messages for an agent")
    p_m_read.add_argument("--agent", required=True, help="Agent name")
    p_m_read.add_argument("--unread-only", action="store_true", help="Return unread messages only")
    p_m_read.add_argument("--leave-unread", action="store_true", help="Do not mark messages as read")

    p_m_log = p_msg_sub.add_parser("log", help="Display global message bus audit log")
    p_m_log.add_argument("--limit", type=int, default=30, help="Max number of messages to show")

    # task
    p_task = subparsers.add_parser("task", help="Task board operations")
    p_task_sub = p_task.add_subparsers(dest="subcommand", required=True)

    p_tk_create = p_task_sub.add_parser("create", help="Create a new task")
    p_tk_create.add_argument("--id", required=True, help="Unique task identifier, e.g. T-1")
    p_tk_create.add_argument("--title", required=True, help="Task title")
    p_tk_create.add_argument("--assignee", required=True, help="Assigned agent name")
    p_tk_create.add_argument("--desc", default="", help="Detailed task instructions")
    p_tk_create.add_argument("--deps", default="", help="Comma-separated prerequisite task IDs")
    p_tk_create.add_argument("--files", default="", help="Comma-separated owned file paths")

    p_tk_update = p_task_sub.add_parser("update", help="Update task status or notes")
    p_tk_update.add_argument("--id", required=True, help="Task ID")
    p_tk_update.add_argument("--status", choices=VALID_STATUSES, help="New status")
    p_tk_update.add_argument("--notes", default=None, help="Progress or review note")
    p_tk_update.add_argument("--assignee", default=None, help="Reassign to another agent")

    p_tk_list = p_task_sub.add_parser("list", help="List tasks")
    p_tk_list.add_argument("--status", choices=VALID_STATUSES, help="Filter by status")
    p_tk_list.add_argument("--assignee", help="Filter by assignee")

    # phase
    p_phase = subparsers.add_parser("phase", help="Set current project phase")
    p_phase.add_argument("name", help="Phase name (e.g. SPECIFICATION, CODING, AUDIT, COMPLETED)")

    # status
    subparsers.add_parser("status", help="Display full team and project dashboard")

    args = parser.parse_args()
    swarm_root = get_swarm_root(args.swarm_dir)

    try:
        if args.command == "init":
            init_workspace(swarm_root, force=args.force)
            if args.json:
                print(json.dumps({"status": "ok", "path": str(swarm_root)}))
            else:
                print(f"[OK] Initialized Swarm workspace at: {swarm_root}")

        elif args.command == "team":
            if args.subcommand == "register":
                res = register_agent(
                    swarm_root,
                    name=args.name,
                    role=args.role,
                    model=args.model,
                    conv_id=args.conv_id
                )
                if args.json:
                    print(json.dumps(res, indent=2))
                else:
                    print(f"[OK] Registered agent '{args.name}' ({args.role}).")

            elif args.subcommand == "list":
                team = get_team(swarm_root)
                if args.json:
                    print(json.dumps(team, indent=2))
                else:
                    print(f"Swarm Team Roster ({len(team)} registered):")
                    for name, meta in team.items():
                        print(f"  - {name:28} | Role: {meta.get('role')} | Tier: {meta.get('model')}")

        elif args.command == "msg":
            if args.subcommand == "send":
                res = send_message(
                    swarm_root,
                    sender=args.sender,
                    recipient=args.recipient,
                    subject=args.subject,
                    body=args.body,
                    msg_type=args.type
                )
                if args.json:
                    print(json.dumps(res, indent=2))
                else:
                    print(f"[OK] Message {res['id']} sent from {args.sender} to {args.recipient}.")

            elif args.subcommand == "broadcast":
                results = broadcast_message(
                    swarm_root,
                    sender=args.sender,
                    subject=args.subject,
                    body=args.body,
                    msg_type=args.type
                )
                if args.json:
                    print(json.dumps(results, indent=2))
                else:
                    print(f"[OK] Broadcast dispatched to {len(results)} team members.")

            elif args.subcommand == "read":
                msgs = read_messages(
                    swarm_root,
                    agent=args.agent,
                    unread_only=args.unread_only,
                    mark_read=not args.leave_unread
                )
                if args.json:
                    print(json.dumps(msgs, indent=2))
                else:
                    if not msgs:
                        print(f"No messages for agent '{args.agent}'.")
                    else:
                        print(f"Messages for '{args.agent}' ({len(msgs)} total):")
                        for m in msgs:
                            print(f"\n[{m['id']}] From: {m['from']} | Type: {m['type']} | Date: {m['timestamp']}")
                            print(f"Subject: {m['subject']}")
                            print(f"Body: {m['body']}")

            elif args.subcommand == "log":
                log = get_bus_log(swarm_root, limit=args.limit)
                if args.json:
                    print(json.dumps(log, indent=2))
                else:
                    print(f"Swarm Message Bus Log (Latest {len(log)}):")
                    for m in log:
                        print(f"[{m.get('timestamp', '')[:19]}] {m.get('from')} -> {m.get('to')}: {m.get('subject')} ({m.get('type')})")

        elif args.command == "task":
            if args.subcommand == "create":
                deps = [d.strip() for d in args.deps.split(",") if d.strip()]
                files = [f.strip() for f in args.files.split(",") if f.strip()]
                task = create_task(
                    swarm_root,
                    task_id=args.id,
                    title=args.title,
                    assignee=args.assignee,
                    description=args.desc,
                    deps=deps,
                    files_owned=files
                )
                if args.json:
                    print(json.dumps(task, indent=2))
                else:
                    print(f"[OK] Task '{args.id}' created and assigned to '{args.assignee}'.")

            elif args.subcommand == "update":
                task = update_task(
                    swarm_root,
                    task_id=args.id,
                    status=args.status,
                    notes=args.notes,
                    assignee=args.assignee
                )
                if args.json:
                    print(json.dumps(task, indent=2))
                else:
                    print(f"[OK] Task '{args.id}' updated. Status: {task['status']}")

            elif args.subcommand == "list":
                tasks = list_tasks(swarm_root, status=args.status, assignee=args.assignee)
                if args.json:
                    print(json.dumps(tasks, indent=2))
                else:
                    print(f"Swarm Task Board ({len(tasks)} tasks):")
                    for t in tasks:
                        dep_str = f" [deps: {','.join(t['deps'])}]" if t.get("deps") else ""
                        files_str = f" [files: {','.join(t['files_owned'])}]" if t.get("files_owned") else ""
                        print(f"  [{t['status']:11}] {t['id']:6} | {t['assignee']:20} | {t['title']}{dep_str}{files_str}")

        elif args.command == "phase":
            new_phase = set_phase(swarm_root, args.name)
            if args.json:
                print(json.dumps({"phase": new_phase}))
            else:
                print(f"[OK] Swarm project phase updated to: {new_phase}")

        elif args.command == "status":
            dash = get_dashboard_status(swarm_root)
            if args.json:
                print(json.dumps(dash, indent=2))
            else:
                print("============================================================")
                print(f"  SWARM ENGINEERING DASHBOARD | PHASE: {dash['phase']}")
                print("============================================================")
                print(f"Team Size: {dash['team_size']} agents")
                for name, meta in dash["team"].items():
                    unread = dash["unread_messages"].get(name, 0)
                    unread_str = f" ({unread} unread msgs)" if unread > 0 else ""
                    print(f"  - {name:26} [{meta.get('role')}]{unread_str}")

                print("\nTask Status Breakdown:")
                for st, count in dash["task_counts"].items():
                    print(f"  - {st:12}: {count}")

                print(f"\nActive Tasks ({dash['total_tasks']}):")
                for t in dash["tasks"]:
                    print(f"  [{t['status']:11}] {t['id']:6} -> {t['assignee']:20} : {t['title']}")
                print("============================================================")

    except Exception as err:
        if args.json:
            print(json.dumps({"error": str(err)}))
        else:
            print(f"[ERROR] {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

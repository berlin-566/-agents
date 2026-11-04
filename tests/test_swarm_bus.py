#!/usr/bin/env python3
"""
Unit tests for swarm_bus.py
"""

import json
import shutil
import tempfile
import unittest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import swarm_bus


class TestSwarmBus(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp(prefix="swarm_test_"))

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_init_workspace(self):
        swarm_bus.init_workspace(self.test_dir)
        self.assertTrue((self.test_dir / "team.json").exists())
        self.assertTrue((self.test_dir / "tasks.json").exists())
        self.assertTrue((self.test_dir / "bus.jsonl").exists())
        self.assertTrue((self.test_dir / "messages").is_dir())
        self.assertTrue((self.test_dir / "contracts").is_dir())

    def test_team_registration(self):
        swarm_bus.init_workspace(self.test_dir)
        agent = swarm_bus.register_agent(
            self.test_dir,
            name="gemini-architect",
            role="Systems Architect",
            model="pro"
        )
        self.assertEqual(agent["name"], "gemini-architect")
        self.assertEqual(agent["role"], "Systems Architect")

        team = swarm_bus.get_team(self.test_dir)
        self.assertIn("gemini-architect", team)

    def test_send_and_read_message(self):
        swarm_bus.init_workspace(self.test_dir)
        swarm_bus.register_agent(self.test_dir, "gemini-architect", "Architect")
        swarm_bus.register_agent(self.test_dir, "gemini-coder", "Engineer")

        # Send message
        msg = swarm_bus.send_message(
            self.test_dir,
            sender="gemini-architect",
            recipient="gemini-coder",
            subject="Architecture Spec",
            body="Review interface contracts in .swarm/contracts/",
            msg_type="handoff"
        )
        self.assertEqual(msg["from"], "gemini-architect")
        self.assertEqual(msg["to"], "gemini-coder")

        # Read unread
        unread = swarm_bus.read_messages(self.test_dir, "gemini-coder", unread_only=True, mark_read=True)
        self.assertEqual(len(unread), 1)
        self.assertEqual(unread[0]["subject"], "Architecture Spec")

        # Subsequent unread check should be empty
        unread_after = swarm_bus.read_messages(self.test_dir, "gemini-coder", unread_only=True)
        self.assertEqual(len(unread_after), 0)

    def test_task_lifecycle(self):
        swarm_bus.init_workspace(self.test_dir)
        task = swarm_bus.create_task(
            self.test_dir,
            task_id="T-01",
            title="Implement Data Layer",
            assignee="gemini-coder",
            files_owned=["src/db.py"]
        )
        self.assertEqual(task["status"], "PENDING")
        self.assertEqual(task["assignee"], "gemini-coder")

        updated = swarm_bus.update_task(
            self.test_dir,
            task_id="T-01",
            status="IN_PROGRESS",
            notes="Started implementation"
        )
        self.assertEqual(updated["status"], "IN_PROGRESS")
        self.assertEqual(len(updated["notes"]), 1)

        tasks = swarm_bus.list_tasks(self.test_dir, status="IN_PROGRESS")
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["id"], "T-01")


if __name__ == "__main__":
    unittest.main()

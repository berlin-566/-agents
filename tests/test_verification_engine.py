#!/usr/bin/env python3
"""
Unit tests for verification_engine.py
Zero-Emoji Policy Enforced.
"""

import json
import shutil
import tempfile
import unittest
from pathlib import Path

import sys
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

import swarm_bus
try:
    from verification_engine import VerificationEngine
except ImportError:
    VerificationEngine = None


class TestVerificationEngine(unittest.TestCase):
    def setUp(self):
        if VerificationEngine is None:
            self.fail("Could not import VerificationEngine from src.verification_engine")
        self.test_dir = Path(tempfile.mkdtemp(prefix="verification_test_"))

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_workspace_integrity_clean(self):
        """Verifies an initialized workspace passes integrity check."""
        swarm_bus.init_workspace(self.test_dir)
        engine = VerificationEngine(self.test_dir)
        result = engine.verify_workspace_integrity()

        self.assertIsInstance(result, dict)
        self.assertTrue(result.get("valid"), f"Expected clean workspace to be valid, got errors: {result.get('errors')}")
        self.assertEqual(len(result.get("errors", [])), 0)

    def test_workspace_integrity_corrupted(self):
        """Verifies missing required components returns valid=False."""
        swarm_bus.init_workspace(self.test_dir)
        # Corrupt the workspace by removing required tasks.json
        tasks_path = self.test_dir / "tasks.json"
        if tasks_path.exists():
            tasks_path.unlink()

        engine = VerificationEngine(self.test_dir)
        result = engine.verify_workspace_integrity()

        self.assertIsInstance(result, dict)
        self.assertFalse(result.get("valid"), "Expected corrupted workspace to fail integrity check")
        self.assertGreater(len(result.get("errors", [])), 0, "Expected error messages for corrupted workspace")

    def test_execute_state_transition_valid(self):
        """Verifies valid transitions (e.g. PENDING -> IN_PROGRESS -> REVIEW)."""
        swarm_bus.init_workspace(self.test_dir)
        swarm_bus.create_task(
            self.test_dir,
            task_id="T-10",
            title="State transition test task",
            assignee="gemini-coder"
        )
        engine = VerificationEngine(self.test_dir)

        # Transition 1: PENDING -> IN_PROGRESS
        updated_1 = engine.execute_state_transition(
            task_id="T-10",
            target_status="IN_PROGRESS",
            actor="gemini-coder",
            note="Agent claimed task"
        )
        self.assertEqual(updated_1["status"], "IN_PROGRESS")

        # Transition 2: IN_PROGRESS -> REVIEW
        updated_2 = engine.execute_state_transition(
            task_id="T-10",
            target_status="REVIEW",
            actor="gemini-coder",
            note="Implementation ready for review"
        )
        self.assertEqual(updated_2["status"], "REVIEW")

        # Transition 3: REVIEW -> PASSED
        updated_3 = engine.execute_state_transition(
            task_id="T-10",
            target_status="PASSED",
            actor="gemini-tester",
            note="QA verification passed"
        )
        self.assertEqual(updated_3["status"], "PASSED")

        # Transition 4: PASSED -> DONE
        updated_4 = engine.execute_state_transition(
            task_id="T-10",
            target_status="DONE",
            actor="gemini-architect",
            note="Final sign-off complete"
        )
        self.assertEqual(updated_4["status"], "DONE")

    def test_execute_state_transition_invalid(self):
        """Verifies invalid transitions raise ValueError."""
        swarm_bus.init_workspace(self.test_dir)
        swarm_bus.create_task(
            self.test_dir,
            task_id="T-20",
            title="Invalid transition test task",
            assignee="gemini-coder"
        )
        engine = VerificationEngine(self.test_dir)

        # Illegal skip: PENDING directly to DONE
        with self.assertRaises(ValueError):
            engine.execute_state_transition(
                task_id="T-20",
                target_status="DONE",
                actor="gemini-coder",
                note="Attempting illegal skip"
            )

        # Illegal skip: PENDING directly to REVIEW
        with self.assertRaises(ValueError):
            engine.execute_state_transition(
                task_id="T-20",
                target_status="REVIEW",
                actor="gemini-coder",
                note="Attempting illegal skip"
            )

        # Completely invalid target status
        with self.assertRaises(ValueError):
            engine.execute_state_transition(
                task_id="T-20",
                target_status="NON_EXISTENT_STATUS",
                actor="gemini-coder",
                note="Invalid target status"
            )

    def test_dispatch_diagnostic(self):
        """Verifies blocker message dispatch onto the swarm bus."""
        swarm_bus.init_workspace(self.test_dir)
        swarm_bus.register_agent(self.test_dir, "gemini-tester", "QA Engineer")
        swarm_bus.register_agent(self.test_dir, "gemini-coder", "Core Developer")

        engine = VerificationEngine(self.test_dir)
        diagnostic_payload = {
            "exit_code": 1,
            "stdout": "Running tests...\nFailed test_example",
            "stderr": "AssertionError: 1 != 0",
            "failed_tests": ["test_example"]
        }

        msg_id = engine.dispatch_diagnostic(
            recipient="gemini-coder",
            subject="QA Failure Diagnostic for Component",
            diagnostic_payload=diagnostic_payload
        )

        self.assertIsInstance(msg_id, str)
        self.assertTrue(len(msg_id) > 0)

        # Verify message arrival in recipient inbox
        messages = swarm_bus.read_messages(
            self.test_dir,
            agent="gemini-coder",
            unread_only=False
        )
        self.assertEqual(len(messages), 1)
        dispatched_msg = messages[0]
        self.assertEqual(dispatched_msg["id"], msg_id)
        self.assertEqual(dispatched_msg["to"], "gemini-coder")
        self.assertEqual(dispatched_msg["type"], "blocker")
        self.assertEqual(dispatched_msg["subject"], "QA Failure Diagnostic for Component")
        self.assertIn("AssertionError", dispatched_msg["body"])


if __name__ == "__main__":
    unittest.main()

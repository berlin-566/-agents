#!/usr/bin/env python3
"""
Unit tests for orchestrator.py
"""

import shutil
import tempfile
import unittest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import orchestrator
import swarm_bus


class TestOrchestrator(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp(prefix="orch_test_"))

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_bootstrap_and_report(self):
        orchestrator.init_project_structure(self.test_dir)
        orchestrator.register_default_team(self.test_dir)
        swarm_bus.set_phase(self.test_dir, "CODING")

        # Create sample task
        swarm_bus.create_task(
            self.test_dir,
            task_id="T-01",
            title="Setup database models",
            assignee="gemini-coder",
            files_owned=["src/models.py"]
        )

        # Generate report
        report_file = orchestrator.generate_delivery_report(self.test_dir)
        self.assertTrue(report_file.exists())

        with open(report_file, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("Swarm Multi-Agent Engineering Delivery Report", content)
        self.assertIn("gemini-architect", content)
        self.assertIn("T-01", content)


if __name__ == "__main__":
    unittest.main()

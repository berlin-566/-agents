#!/usr/bin/env python3
"""
Unit tests for emoji_linter.py
"""

import shutil
import tempfile
import unittest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import emoji_linter


class TestEmojiLinter(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp(prefix="emoji_test_"))

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_clean_text(self):
        clean_text = "def calculate_sum(a: int, b: int) -> int:\n    return a + b\n"
        violations = emoji_linter.scan_text(clean_text, "clean.py")
        self.assertEqual(len(violations), 0)

    def test_emoji_detection(self):
        # Text containing an emoji
        dirty_text = "def calculate():\n    # Function completed \U0001F680\n    return True\n"
        violations = emoji_linter.scan_text(dirty_text, "dirty.py")
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0]["line"], 2)


if __name__ == "__main__":
    unittest.main()

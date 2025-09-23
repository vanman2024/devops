#!/usr/bin/env python3
"""Contract tests for the `ops qa` command."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# Resolve repository root so we can execute the qa command directly
REPO_ROOT = Path(__file__).resolve().parents[2]
QA_COMMAND = REPO_ROOT / "src" / "multiagent_devops" / "ops" / "commands" / "qa.py"


class TestOpsQaContract(unittest.TestCase):
    """End-to-end contract coverage for `ops qa`."""

    def _create_spec(self, name: str) -> Path:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)

        spec_dir = Path(temp_dir.name) / name
        spec_dir.mkdir(parents=True, exist_ok=True)

        # Provide a passing pytest file so the command has something to execute
        (spec_dir / "test_sample.py").write_text(
            """
import pytest


def test_sample_passes():
    assert True
""",
            encoding="utf-8",
        )

        return spec_dir

    def test_ops_qa_successful_run_generates_report(self):
        spec_dir = self._create_spec("happy-spec")

        result = subprocess.run(
            [sys.executable, str(QA_COMMAND), "--spec-path", str(spec_dir)],
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("Running enhanced QA for happy-spec", result.stdout)
        self.assertIn("Tests PASSED", result.stdout)
        self.assertIn("QA report saved to", result.stdout)
        self.assertIn("✅ All QA checks passed!", result.stdout)

        report_path = spec_dir / "qa_report.json"
        self.assertTrue(report_path.exists(), "qa_report.json should be created")

        report_data = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(report_data["spec_name"], "happy-spec")
        self.assertTrue(report_data["tests"]["passed"])
        self.assertEqual(report_data["overall_status"], "PASS")

    def test_ops_qa_handles_missing_spec_path(self):
        missing_path = Path("/nonexistent/spec/path")

        result = subprocess.run(
            [sys.executable, str(QA_COMMAND), "--spec-path", str(missing_path)],
            capture_output=True,
            text=True,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Error: Spec path", result.stderr)

    def test_ops_qa_with_security_and_performance_flags(self):
        spec_dir = self._create_spec("coverage-spec")

        result = subprocess.run(
            [
                sys.executable,
                str(QA_COMMAND),
                "--spec-path",
                str(spec_dir),
                "--security-scan",
                "--performance-test",
                "--coverage-threshold",
                "90",
            ],
            capture_output=True,
            text=True,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Running enhanced QA for coverage-spec", result.stdout)
        self.assertIn("Security scan: True", result.stdout)
        self.assertIn("Performance test: True", result.stdout)
        self.assertIn("Coverage threshold: 90%", result.stdout)
        self.assertIn("Coverage: 85% (FAILED)", result.stdout)
        self.assertIn("❌ QA checks failed", result.stdout)

        report_path = spec_dir / "qa_report.json"
        self.assertTrue(report_path.exists(), "qa_report.json should still be created on failure")

        report_data = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(report_data["overall_status"], "FAIL")
        self.assertTrue(report_data["performance"]["tested"])
        self.assertTrue(report_data["security"]["scanned"])
        self.assertFalse(report_data["coverage"]["passed"])


if __name__ == "__main__":
    unittest.main()

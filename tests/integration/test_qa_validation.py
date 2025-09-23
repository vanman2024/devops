#!/usr/bin/env python3
"""Integration tests for end-to-end QA validation."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
OPS_QA = REPO_ROOT / "src" / "multiagent_devops" / "ops" / "commands" / "qa.py"


class TestQaValidationIntegration(unittest.TestCase):
    """Exercise `ops qa` against real spec content."""

    def _bootstrap_spec(self, spec_name: str) -> Path:
        workspace = Path(tempfile.mkdtemp())
        spec_dir = workspace / spec_name
        spec_dir.mkdir(parents=True, exist_ok=True)

        spec_dir.joinpath("spec.md").write_text(
            """# AI Agent Onboarding

## Summary
Enable automated onboarding for new AI agents.

## Requirements
- Record agent metadata in registry
- Expose onboarding CLI entrypoint

## Acceptance Criteria
- Agent appears in swarm registry with health check enabled
- Founders can run `ops onboarding --dry-run`
""",
            encoding="utf-8",
        )

        test_package = spec_dir / "tests"
        test_package.mkdir(parents=True, exist_ok=True)
        (test_package / "__init__.py").write_text("", encoding="utf-8")
        (test_package / "test_sample.py").write_text(
            """def test_placeholder():
    assert True
""",
            encoding="utf-8",
        )

        self.addCleanup(lambda: subprocess.run(["rm", "-rf", str(workspace)], check=False))
        return spec_dir

    def test_qa_reports_acceptance_criteria_validation(self):
        spec_dir = self._bootstrap_spec("spec-quality")

        result = subprocess.run(
            [sys.executable, str(OPS_QA), "--spec-path", str(spec_dir)],
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("Running enhanced QA for spec-quality", result.stdout)

        report_path = spec_dir / "qa_report.json"
        self.assertTrue(report_path.exists(), "QA run should persist qa_report.json")

        report = json.loads(report_path.read_text(encoding="utf-8"))
        acceptance = report.get("acceptance", {})

        expected_criteria = [
            "Agent appears in swarm registry with health check enabled",
            "Founders can run `ops onboarding --dry-run`",
        ]

        self.assertEqual(acceptance.get("criteria"), expected_criteria)
        self.assertTrue(
            acceptance.get("validated", False),
            "QA report should flag acceptance criteria as validated",
        )


if __name__ == "__main__":
    unittest.main()

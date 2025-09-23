#!/usr/bin/env python3
"""Integration tests for the `ops spec-init` command."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SPEC_INIT = REPO_ROOT / "src" / "multiagent_devops" / "ops" / "commands" / "spec_init.py"


class TestSpecInitIntegration(unittest.TestCase):
    """Exercise the spec-init command end-to-end."""

    def _write_spec(self, spec_dir: Path) -> None:
        spec_content = """# AI Agent Onboarding

## Summary
Enable automated onboarding for new AI agents in the swarm network.

## Requirements
- Provide workspace bootstrapping scripts
- Register agent capabilities with control plane

## Acceptance Criteria
- Agent listed in swarm registry with active health checks
- CLI exposes onboarding command with dry-run mode
"""
        (spec_dir / "spec.md").write_text(spec_content, encoding="utf-8")

    def test_spec_init_parses_spec_and_generates_plan(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            spec_dir = Path(tmp_dir) / "spec-onboarding"
            spec_dir.mkdir(parents=True, exist_ok=True)
            self._write_spec(spec_dir)

            result = subprocess.run(
                [sys.executable, str(SPEC_INIT), "--spec-path", str(spec_dir)],
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertIn("Parsing spec from", result.stdout)
            self.assertIn("Deployment plan generated", result.stdout)
            self.assertIn("CI/CD pipeline configured", result.stdout)

            # Expect real spec title to be surfaced, not placeholder text
            self.assertIn(
                "Spec loaded: AI Agent Onboarding",
                result.stdout,
                msg="spec_init should surface the actual spec title",
            )

            plan_path = spec_dir / "deployment_plan.json"
            self.assertTrue(plan_path.exists(), "spec_init must persist deployment plan")

            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            self.assertEqual(plan["deployment_plan"]["target"], "docker")
            self.assertEqual(plan["deployment_plan"]["environment"], "dev")
            self.assertEqual(plan["ci_cd_pipeline"]["stages"], ["test", "build", "deploy"])
            self.assertEqual(len(plan["qa_checks"]), 6)
            self.assertEqual(plan["status"], "success")

    def test_spec_init_requires_spec_md(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            spec_dir = Path(tmp_dir) / "spec-empty"
            spec_dir.mkdir(parents=True, exist_ok=True)

            result = subprocess.run(
                [sys.executable, str(SPEC_INIT), "--spec-path", str(spec_dir)],
                capture_output=True,
                text=True,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Error: spec.md not found", result.stderr)


if __name__ == "__main__":
    unittest.main()

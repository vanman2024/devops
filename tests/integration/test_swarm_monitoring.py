#!/usr/bin/env python3
"""Integration coverage for swarm logging and rollback behaviour."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SWARM_DEPLOY = REPO_ROOT / "src" / "multiagent_devops" / "ops" / "commands" / "swarm_deploy.py"


class TestSwarmMonitoringIntegration(unittest.TestCase):
    """Verify swarm deployment monitoring artefacts and rollback."""

    def _write_tasks(self, spec_dir: Path, include_tasks: bool = True) -> None:
        spec_dir.mkdir(parents=True, exist_ok=True)
        tasks_md = spec_dir / "tasks.md"
        if include_tasks:
            tasks_md.write_text(
                """## Tasks
- [ ] T001 @codex Build frontend shell
- [ ] T002 @copilot Implement backend service
""",
                encoding="utf-8",
            )
        else:
            tasks_md.write_text("## Tasks\n", encoding="utf-8")

    def test_successful_deploy_creates_monitoring_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            spec_dir = Path(tmp_dir) / "spec-swarm"
            self._write_tasks(spec_dir)

            result = subprocess.run(
                [
                    sys.executable,
                    str(SWARM_DEPLOY),
                    "--spec-path",
                    str(spec_dir),
                    "--agents",
                    "@codex,@copilot",
                ],
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertIn("Swarm status saved", result.stdout)
            self.assertIn("Monitoring snapshot saved", result.stdout)

            status_path = spec_dir / "swarm_status.json"
            monitoring_path = spec_dir / "swarm_monitoring.json"
            log_path = spec_dir / "swarm_log.jsonl"

            self.assertTrue(status_path.exists())
            self.assertTrue(monitoring_path.exists())
            self.assertTrue(log_path.exists())

            status = json.loads(status_path.read_text(encoding="utf-8"))
            self.assertIn("log_path", status)
            self.assertEqual(status["tasks_assigned"], 2)

            monitoring = json.loads(monitoring_path.read_text(encoding="utf-8"))
            self.assertEqual(monitoring["metrics"]["agent_count"], 2)
            self.assertEqual(monitoring["status"], "deployed")

            logs = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines()]
            events = [entry["event"] for entry in logs]
            self.assertIn("start", events)
            self.assertIn("completed", events)

    def test_failed_deploy_rolls_back_status(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            spec_dir = Path(tmp_dir) / "spec-empty"
            self._write_tasks(spec_dir, include_tasks=False)

            result = subprocess.run(
                [sys.executable, str(SWARM_DEPLOY), "--spec-path", str(spec_dir)],
                capture_output=True,
                text=True,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Error: No open tasks", result.stderr)

            self.assertFalse((spec_dir / "swarm_status.json").exists())
            self.assertFalse((spec_dir / "swarm_monitoring.json").exists())

            log_path = spec_dir / "swarm_log.jsonl"
            self.assertTrue(log_path.exists())
            events = [json.loads(line)["event"] for line in log_path.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(events[-1], "rollback")


if __name__ == "__main__":
    unittest.main()

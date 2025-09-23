#!/usr/bin/env python3
"""
Contract test for ops swarm-deploy command
Tests that the swarm-deploy command properly parses tasks and deploys agent swarms.
"""

import unittest
import tempfile
import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

class TestOpsSwarmDeployContract(unittest.TestCase):
    """Contract tests for ops swarm-deploy command"""

    def setUp(self):
        """Set up test fixtures"""
        # Create temporary directory for test spec
        self.test_dir = tempfile.mkdtemp()
        self.spec_path = Path(self.test_dir) / "test-spec"
        self.spec_path.mkdir()
        
        # Create a sample tasks.md file
        self.tasks_file = self.spec_path / "tasks.md"
        self.tasks_content = """# Test Tasks

## Phase 1: Setup
- [ ] T001 @copilot Create test setup
- [ ] T002 @claude Review test setup

## Phase 2: Implementation
- [ ] T003 @qwen Implement feature
- [ ] T004 @gemini Test feature
"""
        self.tasks_file.write_text(self.tasks_content)

    def tearDown(self):
        """Clean up test fixtures"""
        # Remove temporary directory
        import shutil
        shutil.rmtree(self.test_dir)

    def test_swarm_deploy_with_valid_spec(self):
        """Test that swarm-deploy works with valid spec path"""
        from multiagent_devops.ops.commands.swarm_deploy import main
        import subprocess
        import json
        
        # Test by running the command as a subprocess
        cmd = [
            sys.executable, 
            str(Path(__file__).parent.parent.parent / "src/multiagent_devops/ops/commands/swarm_deploy.py"),
            "--spec-path", str(self.spec_path),
            "--agents", "@copilot,@qwen"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Should exit successfully
        self.assertEqual(result.returncode, 0)
        
        # Should contain expected output
        self.assertIn("Deploying swarm with agents: ['@copilot', '@qwen']", result.stdout)
        self.assertIn("Swarm deployed:", result.stdout)
        self.assertIn("Tasks assigned:", result.stdout)
        self.assertIn("Monitoring URL:", result.stdout)
        
        # Should create swarm_status.json
        swarm_status_file = self.spec_path / "swarm_status.json"
        self.assertTrue(swarm_status_file.exists())
        
        # Check swarm status content
        status_data = json.loads(swarm_status_file.read_text())
        self.assertIn("swarm_id", status_data)
        self.assertIn("agents", status_data)
        self.assertEqual(status_data["agents"], ["@copilot", "@qwen"])
        self.assertIn("tasks_assigned", status_data)
        self.assertIn("monitoring_url", status_data)
        self.assertEqual(status_data["status"], "deployed")

    def test_swarm_deploy_missing_spec_path(self):
        """Test that swarm-deploy fails when spec path is missing"""
        from multiagent_devops.ops.commands.swarm_deploy import main
        import subprocess
        
        # Test by running the command as a subprocess without --spec-path
        cmd = [
            sys.executable,
            str(Path(__file__).parent.parent.parent / "src/multiagent_devops/ops/commands/swarm_deploy.py")
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Should exit with error
        self.assertNotEqual(result.returncode, 0)
        
        # Should contain error message about missing spec path
        self.assertIn("error: the following arguments are required: --spec-path", result.stderr)

    def test_swarm_deploy_nonexistent_spec_path(self):
        """Test that swarm-deploy fails when spec path doesn't exist"""
        from multiagent_devops.ops.commands.swarm_deploy import main
        import subprocess
        
        # Test by running the command with non-existent spec path
        cmd = [
            sys.executable,
            str(Path(__file__).parent.parent.parent / "src/multiagent_devops/ops/commands/swarm_deploy.py"),
            "--spec-path", "/non/existent/path"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Should exit with error
        self.assertNotEqual(result.returncode, 0)
        
        # Should contain error message about non-existent path
        self.assertIn("Error: Spec path /non/existent/path does not exist", result.stderr)

    def test_swarm_deploy_missing_tasks_file(self):
        """Test that swarm-deploy fails when tasks.md is missing"""
        from multiagent_devops.ops.commands.swarm_deploy import main
        import subprocess
        
        # Create spec directory without tasks.md
        empty_spec_path = Path(self.test_dir) / "empty-spec"
        empty_spec_path.mkdir()
        
        # Test by running the command with spec path missing tasks.md
        cmd = [
            sys.executable,
            str(Path(__file__).parent.parent.parent / "src/multiagent_devops/ops/commands/swarm_deploy.py"),
            "--spec-path", str(empty_spec_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Should exit with error
        self.assertNotEqual(result.returncode, 0)
        
        # Should contain error message about missing tasks.md
        self.assertIn(f"Error: tasks.md not found in {empty_spec_path}", result.stderr)

if __name__ == "__main__":
    unittest.main()
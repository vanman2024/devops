#!/usr/bin/env python3
"""
Integration test for agent swarm deployment
Tests the end-to-end workflow of deploying agent swarms and verifying their functionality.
"""

import unittest
import tempfile
import os
import sys
import json
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

class TestAgentSwarmDeploymentIntegration(unittest.TestCase):
    """Integration tests for agent swarm deployment"""

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

    def test_swarm_deployment_end_to_end(self):
        """Test complete agent swarm deployment workflow"""
        import subprocess
        
        # Test by running the swarm-deploy command as a subprocess
        cmd = [
            sys.executable, 
            str(Path(__file__).parent.parent.parent / "src/multiagent_devops/ops/commands/swarm_deploy.py"),
            "--spec-path", str(self.spec_path),
            "--agents", "@copilot,@qwen,@claude,@gemini"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Should exit successfully
        self.assertEqual(result.returncode, 0)
        
        # Should contain expected output
        self.assertIn("Deploying swarm with agents: ['@copilot', '@qwen', '@claude', '@gemini']", result.stdout)
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
        self.assertEqual(status_data["agents"], ["@copilot", "@qwen", "@claude", "@gemini"])
        self.assertIn("tasks_assigned", status_data)
        self.assertIn("monitoring_url", status_data)
        self.assertEqual(status_data["status"], "deployed")
        
        # Verify tasks count
        self.assertGreaterEqual(status_data["tasks_assigned"], 4)  # Should have at least 4 tasks

    def test_swarm_deployment_with_default_agents(self):
        """Test swarm deployment with default agents"""
        import subprocess
        
        # Test by running the swarm-deploy command as a subprocess without specifying agents
        cmd = [
            sys.executable, 
            str(Path(__file__).parent.parent.parent / "src/multiagent_devops/ops/commands/swarm_deploy.py"),
            "--spec-path", str(self.spec_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Should exit successfully
        self.assertEqual(result.returncode, 0)
        
        # Should use default agent (@copilot)
        self.assertIn("Deploying swarm with agents: ['@copilot']", result.stdout)
        
        # Should create swarm_status.json
        swarm_status_file = self.spec_path / "swarm_status.json"
        self.assertTrue(swarm_status_file.exists())
        
        # Check swarm status content
        status_data = json.loads(swarm_status_file.read_text())
        self.assertEqual(status_data["agents"], ["@copilot"])

    def test_swarm_deployment_monitoring_integration(self):
        """Test that swarm deployment includes monitoring setup"""
        import subprocess
        
        # Test by running the swarm-deploy command as a subprocess
        cmd = [
            sys.executable, 
            str(Path(__file__).parent.parent.parent / "src/multiagent_devops/ops/commands/swarm_deploy.py"),
            "--spec-path", str(self.spec_path),
            "--agents", "@copilot,@qwen"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Should exit successfully
        self.assertEqual(result.returncode, 0)
        
        # Should provide monitoring URL
        self.assertIn("Monitoring URL:", result.stdout)
        
        # Should create swarm_status.json with monitoring info
        swarm_status_file = self.spec_path / "swarm_status.json"
        self.assertTrue(swarm_status_file.exists())
        
        # Check monitoring URL in status file
        status_data = json.loads(swarm_status_file.read_text())
        self.assertIn("monitoring_url", status_data)
        self.assertTrue(status_data["monitoring_url"].startswith("http://localhost:8000/monitor/"))

    def test_swarm_deployment_logging_integration(self):
        """Test that swarm deployment creates proper logging structure"""
        import subprocess
        
        # Test by running the swarm-deploy command as a subprocess
        cmd = [
            sys.executable, 
            str(Path(__file__).parent.parent.parent / "src/multiagent_devops/ops/commands/swarm_deploy.py"),
            "--spec-path", str(self.spec_path),
            "--agents", "@copilot,@qwen"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Should exit successfully
        self.assertEqual(result.returncode, 0)
        
        # Should create swarm_status.json
        swarm_status_file = self.spec_path / "swarm_status.json"
        self.assertTrue(swarm_status_file.exists())
        
        # Check that status file contains expected structure
        status_data = json.loads(swarm_status_file.read_text())
        self.assertIn("swarm_id", status_data)
        self.assertIn("agents", status_data)
        self.assertIn("tasks_assigned", status_data)
        self.assertIn("monitoring_url", status_data)
        self.assertIn("status", status_data)

    def test_swarm_deployment_error_handling(self):
        """Test swarm deployment error handling with invalid inputs"""
        import subprocess
        
        # Test with non-existent spec path
        cmd = [
            sys.executable, 
            str(Path(__file__).parent.parent.parent / "src/multiagent_devops/ops/commands/swarm_deploy.py"),
            "--spec-path", "/non/existent/path",
            "--agents", "@copilot"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Should exit with error
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Error: Spec path /non/existent/path does not exist", result.stderr)

if __name__ == "__main__":
    unittest.main()
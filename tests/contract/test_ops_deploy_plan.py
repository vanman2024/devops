#!/usr/bin/env python3
"""
Contract test for ops deploy-plan command
Tests that the deploy-plan command properly creates deployment plans for different targets.
"""

import unittest
import tempfile
import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

class TestOpsDeployPlanContract(unittest.TestCase):
    """Contract tests for ops deploy-plan command"""

    def setUp(self):
        """Set up test fixtures"""
        # Create temporary directory for test spec
        self.test_dir = tempfile.mkdtemp()
        self.spec_path = Path(self.test_dir) / "test-spec"
        self.spec_path.mkdir()

    def tearDown(self):
        """Clean up test fixtures"""
        # Remove temporary directory
        import shutil
        shutil.rmtree(self.test_dir)

    def test_deploy_plan_with_docker_target(self):
        """Test that deploy-plan works with docker target"""
        import subprocess
        import json
        
        # Test by running the command as a subprocess
        cmd = [
            sys.executable, 
            str(Path(__file__).parent.parent.parent / "src/multiagent_devops/ops/commands/deploy_plan.py"),
            "--spec-path", str(self.spec_path),
            "--target", "docker",
            "--environment", "dev"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Should exit successfully
        self.assertEqual(result.returncode, 0)
        
        # Should contain expected output
        self.assertIn("Creating deployment plan for docker in dev", result.stdout)
        self.assertIn("Plan created: docker -> dev", result.stdout)
        self.assertIn("Deployment plan saved to", result.stdout)
        self.assertIn("Ready for execution", result.stdout)
        
        # Should create deployment_execution.json
        plan_file = self.spec_path / "deployment_execution.json"
        self.assertTrue(plan_file.exists())
        
        # Check plan content
        plan_data = json.loads(plan_file.read_text())
        self.assertIn("deployment_id", plan_data)
        self.assertIn("target_config", plan_data)
        self.assertIn("rollback_plan", plan_data)
        self.assertEqual(plan_data["status"], "planned")
        
        # Check target config for docker
        target_config = plan_data["target_config"]
        self.assertIn("image", target_config)
        self.assertIn("ports", target_config)
        self.assertIn("volumes", target_config)
        self.assertIn("environment", target_config)
        self.assertEqual(target_config["environment"]["ENV"], "dev")

    def test_deploy_plan_with_azure_target(self):
        """Test that deploy-plan works with azure target"""
        import subprocess
        import json
        
        # Test by running the command as a subprocess
        cmd = [
            sys.executable, 
            str(Path(__file__).parent.parent.parent / "src/multiagent_devops/ops/commands/deploy_plan.py"),
            "--spec-path", str(self.spec_path),
            "--target", "azure",
            "--environment", "staging"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Should exit successfully
        self.assertEqual(result.returncode, 0)
        
        # Should contain expected output
        self.assertIn("Creating deployment plan for azure in staging", result.stdout)
        self.assertIn("Plan created: azure -> staging", result.stdout)
        self.assertIn("Deployment plan saved to", result.stdout)
        self.assertIn("Ready for execution", result.stdout)
        
        # Should create deployment_execution.json
        plan_file = self.spec_path / "deployment_execution.json"
        self.assertTrue(plan_file.exists())
        
        # Check plan content
        plan_data = json.loads(plan_file.read_text())
        self.assertIn("deployment_id", plan_data)
        self.assertIn("target_config", plan_data)
        self.assertIn("rollback_plan", plan_data)
        self.assertEqual(plan_data["status"], "planned")
        
        # Check target config for azure
        target_config = plan_data["target_config"]
        self.assertIn("resource_group", target_config)
        self.assertIn("app_service_plan", target_config)
        self.assertIn("runtime", target_config)
        self.assertIn("environment_variables", target_config)
        self.assertEqual(target_config["environment_variables"]["ENV"], "staging")

    def test_deploy_plan_with_aws_target(self):
        """Test that deploy-plan works with aws target"""
        import subprocess
        import json
        
        # Test by running the command as a subprocess
        cmd = [
            sys.executable, 
            str(Path(__file__).parent.parent.parent / "src/multiagent_devops/ops/commands/deploy_plan.py"),
            "--spec-path", str(self.spec_path),
            "--target", "aws",
            "--environment", "prod"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Should exit successfully
        self.assertEqual(result.returncode, 0)
        
        # Should contain expected output
        self.assertIn("Creating deployment plan for aws in prod", result.stdout)
        self.assertIn("Plan created: aws -> prod", result.stdout)
        self.assertIn("Deployment plan saved to", result.stdout)
        self.assertIn("Ready for execution", result.stdout)
        
        # Should create deployment_execution.json
        plan_file = self.spec_path / "deployment_execution.json"
        self.assertTrue(plan_file.exists())
        
        # Check plan content
        plan_data = json.loads(plan_file.read_text())
        self.assertIn("deployment_id", plan_data)
        self.assertIn("target_config", plan_data)
        self.assertIn("rollback_plan", plan_data)
        self.assertEqual(plan_data["status"], "planned")
        
        # Check target config for aws
        target_config = plan_data["target_config"]
        self.assertIn("region", target_config)
        self.assertIn("instance_type", target_config)
        self.assertIn("ami", target_config)
        self.assertIn("security_groups", target_config)

    def test_deploy_plan_with_script_target(self):
        """Test that deploy-plan works with script target"""
        import subprocess
        import json
        
        # Test by running the command as a subprocess
        cmd = [
            sys.executable, 
            str(Path(__file__).parent.parent.parent / "src/multiagent_devops/ops/commands/deploy_plan.py"),
            "--spec-path", str(self.spec_path),
            "--target", "script",
            "--environment", "dev"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Should exit successfully
        self.assertEqual(result.returncode, 0)
        
        # Should contain expected output
        self.assertIn("Creating deployment plan for script in dev", result.stdout)
        self.assertIn("Plan created: script -> dev", result.stdout)
        self.assertIn("Deployment plan saved to", result.stdout)
        self.assertIn("Ready for execution", result.stdout)
        
        # Should create deployment_execution.json
        plan_file = self.spec_path / "deployment_execution.json"
        self.assertTrue(plan_file.exists())
        
        # Check plan content
        plan_data = json.loads(plan_file.read_text())
        self.assertIn("deployment_id", plan_data)
        self.assertIn("target_config", plan_data)
        self.assertIn("rollback_plan", plan_data)
        self.assertEqual(plan_data["status"], "planned")
        
        # Check target config for script
        target_config = plan_data["target_config"]
        self.assertIn("script_path", target_config)
        self.assertIn("rollback_script", target_config)

    def test_deploy_plan_missing_required_arguments(self):
        """Test that deploy-plan fails when required arguments are missing"""
        import subprocess
        
        # Test by running the command as a subprocess without required arguments
        cmd = [
            sys.executable,
            str(Path(__file__).parent.parent.parent / "src/multiagent_devops/ops/commands/deploy_plan.py")
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Should exit with error
        self.assertNotEqual(result.returncode, 0)
        
        # Should contain error message about missing arguments
        self.assertIn("error: the following arguments are required: --spec-path, --target, --environment", result.stderr)

    def test_deploy_plan_nonexistent_spec_path(self):
        """Test that deploy-plan fails when spec path doesn't exist"""
        import subprocess
        
        # Test by running the command with non-existent spec path
        cmd = [
            sys.executable,
            str(Path(__file__).parent.parent.parent / "src/multiagent_devops/ops/commands/deploy_plan.py"),
            "--spec-path", "/non/existent/path",
            "--target", "docker",
            "--environment", "dev"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Should exit with error
        self.assertNotEqual(result.returncode, 0)
        
        # Should contain error message about non-existent path
        self.assertIn("Error: Spec path /non/existent/path does not exist", result.stderr)

if __name__ == "__main__":
    unittest.main()
#!/usr/bin/env python3
"""
Integration test for deployment with rollback
Tests the end-to-end workflow of deployment plans with rollback capabilities.
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

class TestDeploymentWithRollbackIntegration(unittest.TestCase):
    """Integration tests for deployment with rollback"""

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

    def test_deployment_with_rollback_docker(self):
        """Test complete deployment workflow with rollback for Docker target"""
        import subprocess
        
        # Test by running the deploy-plan command as a subprocess
        cmd = [
            sys.executable, 
            str(Path(__file__).parent.parent.parent / "src/multiagent_devops/ops/commands/deploy_plan.py"),
            "--spec-path", str(self.spec_path),
            "--target", "docker",
            "--environment", "prod"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Should exit successfully
        self.assertEqual(result.returncode, 0)
        
        # Should contain expected output
        self.assertIn("Creating deployment plan for docker in prod", result.stdout)
        self.assertIn("Plan created: docker -> prod", result.stdout)
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
        
        # Check rollback plan
        rollback_plan = plan_data["rollback_plan"]
        self.assertIn("enabled", rollback_plan)
        self.assertTrue(rollback_plan["enabled"])
        self.assertIn("backup_strategy", rollback_plan)
        self.assertEqual(rollback_plan["backup_strategy"], "snapshot")
        self.assertIn("rollback_timeout", rollback_plan)
        self.assertEqual(rollback_plan["rollback_timeout"], 300)
        
        # Check target config for docker
        target_config = plan_data["target_config"]
        self.assertIn("image", target_config)
        self.assertIn("ports", target_config)
        self.assertIn("volumes", target_config)
        self.assertIn("environment", target_config)
        self.assertEqual(target_config["environment"]["ENV"], "prod")
        self.assertEqual(target_config["environment"]["DEBUG"], "false")

    def test_deployment_with_rollback_azure(self):
        """Test complete deployment workflow with rollback for Azure target"""
        import subprocess
        
        # Test by running the deploy-plan command as a subprocess
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
        
        # Check rollback plan
        rollback_plan = plan_data["rollback_plan"]
        self.assertIn("enabled", rollback_plan)
        self.assertTrue(rollback_plan["enabled"])
        self.assertIn("backup_strategy", rollback_plan)
        self.assertEqual(rollback_plan["backup_strategy"], "snapshot")
        self.assertIn("rollback_timeout", rollback_plan)
        self.assertEqual(rollback_plan["rollback_timeout"], 300)
        
        # Check target config for azure
        target_config = plan_data["target_config"]
        self.assertIn("resource_group", target_config)
        self.assertIn("app_service_plan", target_config)
        self.assertIn("runtime", target_config)
        self.assertIn("environment_variables", target_config)
        self.assertEqual(target_config["environment_variables"]["ENV"], "staging")

    def test_deployment_with_rollback_aws(self):
        """Test complete deployment workflow with rollback for AWS target"""
        import subprocess
        
        # Test by running the deploy-plan command as a subprocess
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
        
        # Check rollback plan
        rollback_plan = plan_data["rollback_plan"]
        self.assertIn("enabled", rollback_plan)
        self.assertTrue(rollback_plan["enabled"])
        self.assertIn("backup_strategy", rollback_plan)
        self.assertEqual(rollback_plan["backup_strategy"], "snapshot")
        self.assertIn("rollback_timeout", rollback_plan)
        self.assertEqual(rollback_plan["rollback_timeout"], 300)
        
        # Check target config for aws
        target_config = plan_data["target_config"]
        self.assertIn("region", target_config)
        self.assertIn("instance_type", target_config)
        self.assertIn("ami", target_config)
        self.assertIn("security_groups", target_config)

    def test_deployment_with_rollback_script(self):
        """Test complete deployment workflow with rollback for script target"""
        import subprocess
        
        # Test by running the deploy-plan command as a subprocess
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
        
        # Check rollback plan
        rollback_plan = plan_data["rollback_plan"]
        self.assertIn("enabled", rollback_plan)
        self.assertTrue(rollback_plan["enabled"])
        self.assertIn("backup_strategy", rollback_plan)
        self.assertEqual(rollback_plan["backup_strategy"], "snapshot")
        self.assertIn("rollback_timeout", rollback_plan)
        self.assertEqual(rollback_plan["rollback_timeout"], 300)
        
        # Check target config for script
        target_config = plan_data["target_config"]
        self.assertIn("script_path", target_config)
        self.assertIn("rollback_script", target_config)

    def test_deployment_rollback_disabled_in_dev(self):
        """Test that rollback is properly configured even in dev environments"""
        import subprocess
        
        # Test by running the deploy-plan command as a subprocess
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
        
        # Should create deployment_execution.json
        plan_file = self.spec_path / "deployment_execution.json"
        self.assertTrue(plan_file.exists())
        
        # Check plan content - rollback should still be enabled
        plan_data = json.loads(plan_file.read_text())
        rollback_plan = plan_data["rollback_plan"]
        self.assertIn("enabled", rollback_plan)
        self.assertTrue(rollback_plan["enabled"])  # Rollback is always enabled
        
        # But debug should be true in dev
        target_config = plan_data["target_config"]
        self.assertEqual(target_config["environment"]["DEBUG"], "true")

    def test_deployment_error_handling(self):
        """Test deployment error handling with invalid inputs"""
        import subprocess
        
        # Test with non-existent spec path
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
        self.assertIn("Error: Spec path /non/existent/path does not exist", result.stderr)

if __name__ == "__main__":
    unittest.main()
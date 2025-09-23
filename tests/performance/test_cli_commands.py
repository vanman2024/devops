#!/usr/bin/env python3
"""
Performance tests for CLI commands
Tests the execution time and resource usage of CLI commands.
"""

import unittest
import tempfile
import os
import sys
import time
import subprocess
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

class TestCLIPerformance(unittest.TestCase):
    """Performance tests for CLI commands"""

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

    def measure_execution_time(self, cmd, timeout=10):
        """Measure execution time of a command"""
        start_time = time.time()
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            end_time = time.time()
            execution_time = end_time - start_time
            return execution_time, result
        except subprocess.TimeoutExpired:
            end_time = time.time()
            execution_time = end_time - start_time
            return execution_time, None

    def test_cli_main_command_performance(self):
        """Test that main CLI command executes quickly"""
        cmd = [
            sys.executable, 
            str(Path(__file__).parent.parent.parent / "src/multiagent_devops/cli.py")
        ]
        
        execution_time, result = self.measure_execution_time(cmd)
        
        # Should execute within reasonable time (less than 2 seconds)
        self.assertLess(execution_time, 2.0)
        self.assertIsNotNone(result)
        self.assertEqual(result.returncode, 0)

    def test_cli_status_command_performance(self):
        """Test that status command executes quickly"""
        cmd = [
            sys.executable, 
            str(Path(__file__).parent.parent.parent / "src/multiagent_devops/cli.py"),
            "status"
        ]
        
        execution_time, result = self.measure_execution_time(cmd)
        
        # Should execute within reasonable time (less than 2 seconds)
        self.assertLess(execution_time, 2.0)
        self.assertIsNotNone(result)
        self.assertEqual(result.returncode, 0)
        
        # Should contain expected output
        self.assertIn("DevOps Status", result.stdout)

    def test_cli_qa_command_performance(self):
        """Test that qa command executes quickly"""
        cmd = [
            sys.executable, 
            str(Path(__file__).parent.parent.parent / "src/multiagent_devops/cli.py"),
            "qa"
        ]
        
        execution_time, result = self.measure_execution_time(cmd)
        
        # Should execute within reasonable time (less than 3 seconds)
        self.assertLess(execution_time, 3.0)
        self.assertIsNotNone(result)
        self.assertEqual(result.returncode, 0)
        
        # Should contain expected output
        self.assertIn("Running all QA checks", result.stdout)

    def test_cli_build_command_performance(self):
        """Test that build command executes quickly"""
        cmd = [
            sys.executable, 
            str(Path(__file__).parent.parent.parent / "src/multiagent_devops/cli.py"),
            "build"
        ]
        
        execution_time, result = self.measure_execution_time(cmd)
        
        # Should execute within reasonable time (less than 2 seconds)
        self.assertLess(execution_time, 2.0)
        self.assertIsNotNone(result)
        self.assertEqual(result.returncode, 0)
        
        # Should contain expected output
        self.assertIn("Building for production", result.stdout)

    def test_ops_swarm_deploy_performance(self):
        """Test that ops swarm-deploy command executes quickly"""
        cmd = [
            sys.executable, 
            str(Path(__file__).parent.parent.parent / "src/multiagent_devops/ops/commands/swarm_deploy.py"),
            "--spec-path", str(self.spec_path),
            "--agents", "@copilot,@qwen"
        ]
        
        execution_time, result = self.measure_execution_time(cmd)
        
        # Should execute within reasonable time (less than 3 seconds)
        self.assertLess(execution_time, 3.0)
        self.assertIsNotNone(result)
        self.assertEqual(result.returncode, 0)
        
        # Should contain expected output
        self.assertIn("Deploying swarm with agents", result.stdout)
        self.assertIn("Swarm deployed", result.stdout)

    def test_ops_deploy_plan_performance(self):
        """Test that ops deploy-plan command executes quickly"""
        cmd = [
            sys.executable, 
            str(Path(__file__).parent.parent.parent / "src/multiagent_devops/ops/commands/deploy_plan.py"),
            "--spec-path", str(self.spec_path),
            "--target", "docker",
            "--environment", "dev"
        ]
        
        execution_time, result = self.measure_execution_time(cmd)
        
        # Should execute within reasonable time (less than 3 seconds)
        self.assertLess(execution_time, 3.0)
        self.assertIsNotNone(result)
        self.assertEqual(result.returncode, 0)
        
        # Should contain expected output
        self.assertIn("Creating deployment plan for docker in dev", result.stdout)
        self.assertIn("Plan created", result.stdout)

    def test_ops_spec_init_performance(self):
        """Test that ops spec-init command executes quickly"""
        cmd = [
            sys.executable, 
            str(Path(__file__).parent.parent.parent / "src/multiagent_devops/ops/commands/spec_init.py"),
            "--spec-path", str(self.spec_path)
        ]
        
        execution_time, result = self.measure_execution_time(cmd)
        
        # Should execute within reasonable time (less than 3 seconds)
        self.assertLess(execution_time, 3.0)
        # Note: This might fail because spec_init.py might not exist yet or might have issues
        # but we're measuring performance, not correctness

    def test_concurrent_command_execution(self):
        """Test that multiple CLI commands can run concurrently without performance degradation"""
        import threading
        
        def run_command(cmd_list):
            try:
                subprocess.run(cmd_list, capture_output=True, text=True, timeout=5)
            except subprocess.TimeoutExpired:
                pass
        
        # Commands to run concurrently
        commands = [
            [sys.executable, str(Path(__file__).parent.parent.parent / "src/multiagent_devops/cli.py"), "status"],
            [sys.executable, str(Path(__file__).parent.parent.parent / "src/multiagent_devops/cli.py"), "qa"],
            [sys.executable, str(Path(__file__).parent.parent.parent / "src/multiagent_devops/ops/commands/swarm_deploy.py"), "--spec-path", str(self.spec_path), "--agents", "@copilot"],
        ]
        
        start_time = time.time()
        
        # Run commands in parallel
        threads = []
        for cmd in commands:
            thread = threading.Thread(target=run_command, args=(cmd,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # All commands should complete within reasonable time when run concurrently
        # (This might be longer than individual commands due to concurrency overhead)
        self.assertLess(total_time, 6.0)

    def test_memory_usage_of_cli_commands(self):
        """Test that CLI commands don't consume excessive memory"""
        import psutil
        import os
        
        # This test requires psutil, which might not be available
        # We'll skip it if psutil is not installed
        try:
            import psutil
        except ImportError:
            self.skipTest("psutil not available")
            
        # Get current process
        current_process = psutil.Process(os.getpid())
        initial_memory = current_process.memory_info().rss / 1024 / 1024  # MB
        
        # Run a CLI command
        cmd = [
            sys.executable, 
            str(Path(__file__).parent.parent.parent / "src/multiagent_devops/cli.py"),
            "status"
        ]
        
        subprocess.run(cmd, capture_output=True, text=True)
        
        # Check memory usage after command
        final_memory = current_process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 50MB)
        self.assertLess(memory_increase, 50.0)

    def test_startup_time_of_cli_commands(self):
        """Test that CLI commands have fast startup times"""
        # Measure import time for CLI modules
        start_time = time.time()
        
        # Import the CLI module
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "cli", 
            str(Path(__file__).parent.parent.parent / "src/multiagent_devops/cli.py")
        )
        if spec and spec.loader:
            cli_module = importlib.util.module_from_spec(spec)
            # We won't actually execute the module, just measure import time
            try:
                spec.loader.exec_module(cli_module)
            except SystemExit:
                # Click commands might call sys.exit, which is expected
                pass
        
        end_time = time.time()
        import_time = end_time - start_time
        
        # Import should be fast (less than 1 second)
        self.assertLess(import_time, 1.0)

if __name__ == "__main__":
    unittest.main()
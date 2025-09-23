#!/usr/bin/env python3
"""
Unit tests for all models in multiagent_devops
Tests model creation, validation, and methods
"""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from multiagent_devops.models import (
    Spec, Task, AgentSwarm, DeploymentPlan, QAReport
)


class TestSpecModel:
    """Unit tests for Spec model"""
    
    def test_spec_creation(self):
        """Test basic Spec model creation"""
        spec = Spec(
            name="test-feature",
            version="1.0.0",
            description="Test feature spec",
            tasks=[]
        )
        
        assert spec.name == "test-feature"
        assert spec.version == "1.0.0"
        assert spec.description == "Test feature spec"
        assert spec.tasks == []
    
    def test_spec_from_spec_file(self, tmp_path):
        """Test creating Spec from spec.md file"""
        spec_file = tmp_path / "spec.md"
        spec_file.write_text("""
# Feature: User Authentication

## Description
User authentication system with email/password

## Requirements
- FR-001: Login with email
- FR-002: Password reset
        """)
        
        spec = Spec.from_spec_file(str(spec_file))
        
        assert spec.name == "User Authentication"
        assert "authentication" in spec.description.lower()
        assert len(spec.requirements) > 0
    
    def test_spec_validation(self):
        """Test Spec validation"""
        # Valid spec
        spec = Spec(
            name="valid-spec",
            version="1.0.0",
            description="Valid spec",
            tasks=["task1", "task2"]
        )
        assert spec.is_valid()
        
        # Invalid spec - missing name
        spec_invalid = Spec(
            name="",
            version="1.0.0",
            description="Invalid spec",
            tasks=[]
        )
        assert not spec_invalid.is_valid()
    
    def test_spec_to_dict(self):
        """Test converting Spec to dictionary"""
        spec = Spec(
            name="test-spec",
            version="1.0.0",
            description="Test spec",
            tasks=["task1"],
            requirements={"FR-001": "Test requirement"}
        )
        
        spec_dict = spec.to_dict()
        
        assert spec_dict["name"] == "test-spec"
        assert spec_dict["version"] == "1.0.0"
        assert spec_dict["description"] == "Test spec"
        assert len(spec_dict["tasks"]) == 1
        assert "FR-001" in spec_dict["requirements"]
    
    def test_spec_from_dict(self):
        """Test creating Spec from dictionary"""
        data = {
            "name": "from-dict",
            "version": "2.0.0",
            "description": "Created from dict",
            "tasks": ["task1", "task2"],
            "requirements": {"FR-001": "Requirement 1"}
        }
        
        spec = Spec.from_dict(data)
        
        assert spec.name == "from-dict"
        assert spec.version == "2.0.0"
        assert len(spec.tasks) == 2
        assert "FR-001" in spec.requirements


class TestTaskModel:
    """Unit tests for Task model"""
    
    def test_task_creation(self):
        """Test Task model creation"""
        task = Task(
            id="T001",
            description="Implement login",
            agent="@copilot",
            status="pending"
        )
        
        assert task.id == "T001"
        assert task.description == "Implement login"
        assert task.agent == "@copilot"
        assert task.status == "pending"
        assert task.parallel is False
    
    def test_task_with_dependencies(self):
        """Test Task with dependencies"""
        task = Task(
            id="T002",
            description="Deploy to production",
            agent="@claude",
            dependencies=["T001"],
            parallel=True
        )
        
        assert len(task.dependencies) == 1
        assert "T001" in task.dependencies
        assert task.parallel is True
    
    def test_task_status_update(self):
        """Test updating task status"""
        task = Task(
            id="T003",
            description="Write tests",
            agent="@qwen",
            status="pending"
        )
        
        task.update_status("in_progress")
        assert task.status == "in_progress"
        
        task.update_status("completed")
        assert task.status == "completed"
        
        # Invalid status should not update
        task.update_status("invalid_status")
        assert task.status == "completed"
    
    def test_task_from_markdown_line(self):
        """Test creating Task from markdown line"""
        line = "- [ ] T004 [P] @claude Design architecture in src/architecture.py"
        
        task = Task.from_markdown_line(line)
        
        assert task.id == "T004"
        assert task.agent == "@claude"
        assert task.description == "Design architecture"
        assert task.file_path == "src/architecture.py"
        assert task.parallel is True
        assert task.status == "pending"
    
    def test_task_to_markdown(self):
        """Test converting Task to markdown line"""
        task = Task(
            id="T005",
            description="Create API endpoint",
            agent="@copilot",
            file_path="src/api.py",
            parallel=True,
            status="completed"
        )
        
        markdown = task.to_markdown()
        
        assert "- [x]" in markdown  # Completed
        assert "T005" in markdown
        assert "[P]" in markdown  # Parallel
        assert "@copilot" in markdown
        assert "Create API endpoint" in markdown
        assert "src/api.py" in markdown


class TestAgentSwarmModel:
    """Unit tests for AgentSwarm model"""
    
    def test_agent_swarm_creation(self):
        """Test AgentSwarm model creation"""
        swarm = AgentSwarm(
            name="test-swarm",
            agents=["@copilot", "@claude"],
            config={"parallel": True}
        )
        
        assert swarm.name == "test-swarm"
        assert len(swarm.agents) == 2
        assert "@copilot" in swarm.agents
        assert swarm.config["parallel"] is True
    
    def test_agent_swarm_with_tasks(self):
        """Test AgentSwarm with tasks"""
        task1 = Task("T001", "Task 1", "@copilot")
        task2 = Task("T002", "Task 2", "@claude")
        
        swarm = AgentSwarm(
            name="swarm-with-tasks",
            agents=["@copilot", "@claude"],
            tasks=[task1, task2]
        )
        
        assert len(swarm.tasks) == 2
        assert swarm.tasks[0].id == "T001"
        assert swarm.tasks[1].agent == "@claude"
    
    def test_agent_workload_calculation(self):
        """Test calculating agent workload"""
        task1 = Task("T001", "Task 1", "@copilot")
        task2 = Task("T002", "Task 2", "@copilot")
        task3 = Task("T003", "Task 3", "@claude")
        
        swarm = AgentSwarm(
            name="workload-test",
            agents=["@copilot", "@claude"],
            tasks=[task1, task2, task3]
        )
        
        workload = swarm.get_agent_workload()
        
        assert workload["@copilot"] == 2  # 2 tasks
        assert workload["@claude"] == 1   # 1 task
    
    def test_agent_swarm_to_yaml(self):
        """Test converting AgentSwarm to YAML format"""
        swarm = AgentSwarm(
            name="yaml-swarm",
            agents=["@copilot", "@codex"],
            config={
                "parallel_execution": True,
                "monitoring": True
            }
        )
        
        yaml_str = swarm.to_yaml()
        
        assert "name: yaml-swarm" in yaml_str
        assert "@copilot" in yaml_str or "copilot" in yaml_str
        assert "parallel_execution: true" in yaml_str.lower()
    
    def test_agent_swarm_deploy(self):
        """Test deploying agent swarm"""
        swarm = AgentSwarm(
            name="deploy-swarm",
            agents=["@copilot"],
            config={"auto_retry": True}
        )
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout="deployed")
            
            result = swarm.deploy()
            
            assert result is True
            mock_run.assert_called()


class TestDeploymentPlanModel:
    """Unit tests for DeploymentPlan model"""
    
    def test_deployment_plan_creation(self):
        """Test DeploymentPlan model creation"""
        plan = DeploymentPlan(
            target="docker",
            environment="production",
            config={"auto_rollback": True}
        )
        
        assert plan.target == "docker"
        assert plan.environment == "production"
        assert plan.config["auto_rollback"] is True
    
    def test_deployment_plan_from_spec(self):
        """Test creating DeploymentPlan from Spec"""
        spec = Spec(
            name="test-spec",
            version="1.0.0",
            description="Docker-based application",
            requirements={"deployment": "kubernetes"}
        )
        
        plan = DeploymentPlan.from_spec(spec)
        
        assert plan.target in ["docker", "kubernetes"]
        assert plan.environment in ["dev", "staging", "production"]
        assert "rollback_enabled" in plan.config
    
    def test_deployment_plan_stages(self):
        """Test deployment stages"""
        plan = DeploymentPlan(
            target="kubernetes",
            environment="staging",
            stages=["build", "test", "deploy", "verify"]
        )
        
        assert len(plan.stages) == 4
        assert "build" in plan.stages
        assert "verify" in plan.stages
    
    def test_deployment_plan_validation(self):
        """Test deployment plan validation"""
        # Valid plan
        plan = DeploymentPlan(
            target="docker",
            environment="production"
        )
        assert plan.is_valid()
        
        # Invalid target
        plan_invalid = DeploymentPlan(
            target="invalid_target",
            environment="production"
        )
        assert not plan_invalid.is_valid()
    
    def test_deployment_plan_execute(self):
        """Test executing deployment plan"""
        plan = DeploymentPlan(
            target="docker",
            environment="dev",
            config={"dry_run": True}
        )
        
        with patch('multiagent_devops.deploy.executor.execute_plan') as mock_execute:
            mock_execute.return_value = {"status": "success"}
            
            result = plan.execute()
            
            assert result["status"] == "success"
            mock_execute.assert_called_once()


class TestQAReportModel:
    """Unit tests for QAReport model"""
    
    def test_qa_report_creation(self):
        """Test QAReport model creation"""
        report = QAReport(
            spec_name="test-spec",
            timestamp="2024-01-01T00:00:00",
            results={}
        )
        
        assert report.spec_name == "test-spec"
        assert report.timestamp == "2024-01-01T00:00:00"
        assert report.results == {}
    
    def test_qa_report_add_result(self):
        """Test adding results to QA report"""
        report = QAReport(
            spec_name="test-spec",
            timestamp="2024-01-01T00:00:00"
        )
        
        report.add_result("linting", {"status": "passed", "errors": 0})
        report.add_result("tests", {"status": "passed", "coverage": 85})
        
        assert "linting" in report.results
        assert report.results["linting"]["status"] == "passed"
        assert report.results["tests"]["coverage"] == 85
    
    def test_qa_report_summary(self):
        """Test QA report summary generation"""
        report = QAReport(
            spec_name="test-spec",
            timestamp="2024-01-01T00:00:00"
        )
        
        report.add_result("linting", {"status": "passed"})
        report.add_result("tests", {"status": "failed", "failures": 2})
        report.add_result("security", {"status": "passed"})
        
        summary = report.get_summary()
        
        assert summary["total_checks"] == 3
        assert summary["passed"] == 2
        assert summary["failed"] == 1
        assert summary["overall_status"] == "failed"
    
    def test_qa_report_to_json(self):
        """Test converting QA report to JSON"""
        report = QAReport(
            spec_name="json-spec",
            timestamp="2024-01-01T00:00:00"
        )
        
        report.add_result("linting", {"status": "passed"})
        
        json_str = report.to_json()
        data = json.loads(json_str)
        
        assert data["spec_name"] == "json-spec"
        assert "linting" in data["results"]
    
    def test_qa_report_from_file(self, tmp_path):
        """Test loading QA report from file"""
        report_file = tmp_path / "qa_report.json"
        report_data = {
            "spec_name": "file-spec",
            "timestamp": "2024-01-01T00:00:00",
            "results": {
                "tests": {"status": "passed", "coverage": 90}
            }
        }
        report_file.write_text(json.dumps(report_data))
        
        report = QAReport.from_file(str(report_file))
        
        assert report.spec_name == "file-spec"
        assert report.results["tests"]["coverage"] == 90


class TestModelIntegration:
    """Integration tests for models working together"""
    
    def test_spec_to_deployment_flow(self):
        """Test flow from Spec to DeploymentPlan"""
        spec = Spec(
            name="integration-spec",
            version="1.0.0",
            description="Full integration test",
            tasks=[
                Task("T001", "Setup", "@copilot"),
                Task("T002", "Deploy", "@claude")
            ]
        )
        
        plan = DeploymentPlan.from_spec(spec)
        
        assert plan is not None
        assert plan.target in ["docker", "kubernetes", "serverless", "vps"]
    
    def test_task_to_swarm_assignment(self):
        """Test assigning tasks to agent swarm"""
        tasks = [
            Task("T001", "Backend API", "@copilot"),
            Task("T002", "Frontend UI", "@codex"),
            Task("T003", "Security Review", "@claude")
        ]
        
        swarm = AgentSwarm(
            name="task-assignment",
            agents=["@copilot", "@codex", "@claude"],
            tasks=tasks
        )
        
        workload = swarm.get_agent_workload()
        
        assert workload["@copilot"] == 1
        assert workload["@codex"] == 1
        assert workload["@claude"] == 1
    
    def test_qa_report_for_spec(self):
        """Test generating QA report for a spec"""
        spec = Spec(
            name="qa-test-spec",
            version="1.0.0",
            description="QA test spec"
        )
        
        report = QAReport.from_spec(spec)
        
        # Run QA checks (mocked)
        report.add_result("linting", {"status": "passed"})
        report.add_result("tests", {"status": "passed", "coverage": 95})
        report.add_result("security", {"status": "passed"})
        
        summary = report.get_summary()
        
        assert summary["overall_status"] == "passed"
        assert summary["passed"] == 3
        assert summary["failed"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
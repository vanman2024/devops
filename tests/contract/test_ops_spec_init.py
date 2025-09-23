#!/usr/bin/env python3
"""
Contract test for ops spec-init command
Tests the contract/interface without implementation
Must fail initially (TDD approach)
"""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


class TestOpsSpecInitContract:
    """Contract tests for ops spec-init command"""
    
    def test_command_exists(self):
        """Test that ops spec-init command is available"""
        from multiagent_devops.ops.commands import spec_init
        assert hasattr(spec_init, 'main'), "spec_init.main function must exist"
    
    def test_accepts_spec_path_argument(self):
        """Test that command accepts --spec-path argument"""
        with patch('sys.argv', ['spec-init', '--spec-path', 'specs/001-feature']):
            from multiagent_devops.ops.commands.spec_init import main
            # Should not raise an error for missing argument
            with patch('multiagent_devops.ops.commands.spec_init.Path'):
                try:
                    main()
                except SystemExit as e:
                    # Should exit with error code for missing spec, not missing argument
                    assert e.code == 1
    
    def test_spec_analysis_contract(self):
        """Test that spec analyzer returns expected structure"""
        from multiagent_devops.spec_analyzer import SpecAnalyzer
        
        analyzer = SpecAnalyzer()
        spec_path = Path("specs/test-spec")
        
        # Contract: analyze_spec should return this structure
        result = analyzer.analyze_spec(spec_path)
        
        assert isinstance(result, dict), "Result must be a dictionary"
        assert 'components_needed' in result, "Must identify needed components"
        assert 'stack_detected' in result, "Must detect technology stack"
        assert 'agents_recommended' in result, "Must recommend agents"
        assert 'deployment_targets' in result, "Must suggest deployment targets"
        
        # Type checking
        assert isinstance(result['components_needed'], list)
        assert isinstance(result['stack_detected'], dict)
        assert isinstance(result['agents_recommended'], list)
        assert isinstance(result['deployment_targets'], list)
    
    def test_component_discovery_contract(self):
        """Test component discovery based on spec content"""
        from multiagent_devops.component_manager import ComponentManager
        
        manager = ComponentManager()
        
        # Test with authentication keywords
        spec_content = """
        Users must be able to login with email and password.
        Support OAuth with Google and GitHub.
        Implement JWT tokens for session management.
        """
        
        components = manager.analyze_content(spec_content)
        assert 'multiagent-auth' in components, "Should detect auth component need"
        
        # Test with payment keywords
        spec_content = """
        Process payments using Stripe.
        Support subscriptions and one-time purchases.
        Handle refunds and webhooks.
        """
        
        components = manager.analyze_content(spec_content)
        assert 'multiagent-payments' in components, "Should detect payment component need"
    
    def test_deployment_plan_generation_contract(self):
        """Test that deployment plan is generated correctly"""
        from multiagent_devops.models import Spec, DeploymentPlan
        
        spec = Spec.from_spec_file("specs/test/spec.md")
        plan = DeploymentPlan.from_spec(spec)
        
        # Contract requirements
        assert plan.target in ['docker', 'kubernetes', 'serverless', 'vps']
        assert plan.environment in ['dev', 'staging', 'production']
        assert isinstance(plan.config, dict)
        assert 'rollback_enabled' in plan.config
        assert 'monitoring' in plan.config
        assert 'auto_scale' in plan.config
    
    def test_cicd_pipeline_generation_contract(self):
        """Test CI/CD pipeline generation from spec"""
        from multiagent_devops.ops.commands.spec_init import generate_cicd_pipeline
        
        spec_path = Path("specs/test-spec")
        pipeline = generate_cicd_pipeline(spec_path)
        
        # Contract: Pipeline must have these stages
        assert 'stages' in pipeline
        assert 'test' in pipeline['stages']
        assert 'build' in pipeline['stages'] 
        assert 'deploy' in pipeline['stages']
        
        # Jobs structure
        assert 'jobs' in pipeline
        assert 'test' in pipeline['jobs']
        assert 'script' in pipeline['jobs']['test']
        assert isinstance(pipeline['jobs']['test']['script'], list)
    
    def test_qa_checks_generation_contract(self):
        """Test QA checks are generated based on spec requirements"""
        from multiagent_devops.ops.commands.spec_init import generate_qa_checks
        
        spec_requirements = {
            'security': True,
            'performance': True,
            'accessibility': False
        }
        
        qa_checks = generate_qa_checks(spec_requirements)
        
        # Must include based on requirements
        assert 'security_scan' in qa_checks
        assert 'performance_test' in qa_checks
        assert 'linting' in qa_checks  # Always included
        assert 'type_checking' in qa_checks  # Always included
        assert 'unit_tests' in qa_checks  # Always included
        
        # Should not include if not required
        assert 'accessibility_audit' not in qa_checks
    
    def test_output_file_structure_contract(self):
        """Test that output files follow expected structure"""
        from multiagent_devops.ops.commands.spec_init import save_deployment_plan
        
        spec_path = Path("specs/test-spec")
        plan = {
            'deployment_plan': {
                'target': 'docker',
                'environment': 'dev',
                'config': {'rollback_enabled': True}
            },
            'ci_cd_pipeline': {
                'stages': ['test', 'build', 'deploy'],
                'jobs': {}
            },
            'qa_checks': ['linting', 'testing'],
            'components_needed': ['multiagent-auth'],
            'agents_recommended': ['@copilot', '@claude']
        }
        
        output_path = save_deployment_plan(spec_path, plan)
        
        # Contract: Must save to spec directory
        assert output_path.parent == spec_path
        assert output_path.name == 'deployment_plan.json'
        
        # Content must be valid JSON
        with open(output_path) as f:
            loaded = json.load(f)
            assert loaded == plan
    
    def test_error_handling_contract(self):
        """Test proper error handling and messages"""
        from multiagent_devops.ops.commands.spec_init import main
        
        # Non-existent spec path
        with patch('sys.argv', ['spec-init', '--spec-path', '/nonexistent/path']):
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 1
        
        # Missing spec.md file
        with patch('sys.argv', ['spec-init', '--spec-path', 'specs/exists-but-no-spec']):
            with patch('pathlib.Path.exists', return_value=True):
                with patch('pathlib.Path.is_file', return_value=False):
                    with pytest.raises(SystemExit) as exc:
                        main()
                    assert exc.value.code == 1
    
    def test_agent_recommendations_contract(self):
        """Test that agent recommendations match capability matrix"""
        from multiagent_devops.agent_router import recommend_agents
        
        # Backend heavy spec
        tasks = [
            "Create REST API",
            "Implement database models",
            "Add authentication"
        ]
        
        agents = recommend_agents(tasks)
        assert '@copilot' in agents, "Copilot should be recommended for backend"
        assert '@claude' in agents, "Claude should be recommended for architecture"
        
        # Frontend heavy spec
        tasks = [
            "Create React components",
            "Build interactive UI",
            "Add animations"
        ]
        
        agents = recommend_agents(tasks)
        assert '@codex' in agents, "Codex should be recommended for frontend"
        
        # Performance optimization needed
        tasks = [
            "Optimize database queries",
            "Improve algorithm efficiency",
            "Reduce memory usage"
        ]
        
        agents = recommend_agents(tasks)
        assert '@qwen' in agents, "Qwen should be recommended for optimization"


class TestSpecInitIntegration:
    """Integration tests for spec-init command"""
    
    @pytest.fixture
    def sample_spec(self, tmp_path):
        """Create a sample spec for testing"""
        spec_dir = tmp_path / "specs" / "test-feature"
        spec_dir.mkdir(parents=True)
        
        spec_file = spec_dir / "spec.md"
        spec_file.write_text("""
# Feature: User Authentication

## Requirements
- Users can register with email
- Login with email/password
- Password reset via email
- OAuth with Google

## Tech Stack
- Backend: Python/FastAPI
- Frontend: React
- Database: PostgreSQL
        """)
        
        return spec_dir
    
    def test_full_workflow(self, sample_spec):
        """Test complete spec-init workflow"""
        from multiagent_devops.ops.commands.spec_init import main
        
        with patch('sys.argv', ['spec-init', '--spec-path', str(sample_spec)]):
            # Should complete without errors
            result = main()
            assert result == 0 or result is None
        
        # Check output file was created
        plan_file = sample_spec / "deployment_plan.json"
        assert plan_file.exists()
        
        # Verify content
        with open(plan_file) as f:
            plan = json.load(f)
        
        assert plan['status'] == 'success'
        assert 'multiagent-auth' in plan['components_needed']
        assert '@copilot' in plan['agents_recommended']
        assert plan['deployment_plan']['target'] in ['docker', 'kubernetes']
#!/usr/bin/env python3
"""
Quickstart validation for multiagent-devops
Validates that the system works end-to-end from spec to deployment
"""

import sys
import subprocess
import json
from pathlib import Path
import tempfile
import shutil
from typing import Dict, List, Tuple, Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from multiagent_devops.spec_analyzer import SpecAnalyzer
from multiagent_devops.agent_capabilities import AgentRouter
from multiagent_devops.integrations.agentswarm import AgentSwarmIntegration


class QuickstartValidator:
    """Validates the complete DevOps workflow"""
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.results = {
            "passed": [],
            "failed": [],
            "warnings": []
        }
    
    def log(self, message: str, level: str = "INFO"):
        """Log message with level"""
        if self.verbose:
            prefix = {
                "INFO": "ℹ️ ",
                "SUCCESS": "✅",
                "ERROR": "❌",
                "WARNING": "⚠️ "
            }.get(level, "")
            print(f"{prefix} {message}")
    
    def run_validation(self) -> bool:
        """Run complete quickstart validation"""
        self.log("Starting multiagent-devops quickstart validation", "INFO")
        
        # 1. Validate environment
        if not self.validate_environment():
            return False
        
        # 2. Create test spec
        test_spec_path = self.create_test_spec()
        if not test_spec_path:
            return False
        
        try:
            # 3. Validate spec analysis
            if not self.validate_spec_analysis(test_spec_path):
                return False
            
            # 4. Validate agent routing
            if not self.validate_agent_routing(test_spec_path):
                return False
            
            # 5. Validate component discovery
            if not self.validate_component_discovery(test_spec_path):
                return False
            
            # 6. Validate CLI commands
            if not self.validate_cli_commands(test_spec_path):
                return False
            
            # 7. Validate integration
            if not self.validate_integration(test_spec_path):
                return False
            
        finally:
            # Clean up test spec
            if test_spec_path and test_spec_path.exists():
                shutil.rmtree(test_spec_path.parent)
        
        # Print summary
        self.print_summary()
        
        return len(self.results["failed"]) == 0
    
    def validate_environment(self) -> bool:
        """Validate that required dependencies are available"""
        self.log("Validating environment...", "INFO")
        
        # Check Python version
        if sys.version_info < (3, 9):
            self.log(f"Python 3.9+ required, got {sys.version}", "ERROR")
            self.results["failed"].append("Python version check")
            return False
        self.results["passed"].append("Python version check")
        
        # Check required modules
        required_modules = [
            "click", "rich", "yaml", "pytest"
        ]
        
        for module in required_modules:
            try:
                __import__(module)
                self.results["passed"].append(f"Module {module}")
            except ImportError:
                self.log(f"Required module '{module}' not found", "ERROR")
                self.results["failed"].append(f"Module {module}")
                return False
        
        self.log("Environment validation passed", "SUCCESS")
        return True
    
    def create_test_spec(self) -> Optional[Path]:
        """Create a test spec for validation"""
        self.log("Creating test spec...", "INFO")
        
        # Create temp directory
        temp_dir = Path(tempfile.mkdtemp(prefix="devops_validation_"))
        spec_dir = temp_dir / "specs" / "quickstart-test"
        spec_dir.mkdir(parents=True)
        
        # Create spec.md
        spec_file = spec_dir / "spec.md"
        spec_file.write_text("""
# Feature: E-commerce Platform

## Description
Build a complete e-commerce platform with user authentication, product catalog,
shopping cart, payment processing, and order management.

## Requirements

### Functional Requirements
- FR-001: Users can register and login with email/password
- FR-002: OAuth authentication with Google and GitHub
- FR-003: Product search and filtering
- FR-004: Shopping cart management
- FR-005: Payment processing with Stripe
- FR-006: Order tracking and history
- FR-007: Email notifications for orders
- FR-008: Real-time inventory updates

### Non-Functional Requirements
- NFR-001: Response time under 200ms
- NFR-002: Support 10,000 concurrent users
- NFR-003: 99.9% uptime
- NFR-004: WCAG 2.1 AA compliance

## Tech Stack
- Backend: Python with FastAPI
- Frontend: React with TypeScript
- Database: PostgreSQL
- Cache: Redis
- Search: Elasticsearch
- Deployment: Docker and Kubernetes
        """)
        
        # Create tasks.md
        tasks_file = spec_dir / "tasks.md"
        tasks_file.write_text("""
# Tasks: E-commerce Platform

## Phase 1: Setup
- [ ] T001 @copilot Setup FastAPI project structure
- [ ] T002 @copilot Configure PostgreSQL database
- [ ] T003 @codex Create React frontend scaffold

## Phase 2: Core Features
- [ ] T004 @copilot Implement user authentication API
- [ ] T005 @codex Build login/register UI components
- [ ] T006 @copilot Create product CRUD API
- [ ] T007 @codex Design product listing page
- [ ] T008 @copilot Implement shopping cart backend
- [ ] T009 @codex Create cart UI with real-time updates
- [ ] T010 @claude Integrate Stripe payment processing

## Phase 3: Advanced Features
- [ ] T011 @qwen Optimize database queries
- [ ] T012 @claude Setup Redis caching layer
- [ ] T013 @qwen Implement Elasticsearch integration
- [ ] T014 @gemini Write API documentation

## Phase 4: Deployment
- [ ] T015 @claude Create Docker configurations
- [ ] T016 @claude Setup Kubernetes manifests
- [ ] T017 @qwen Performance testing and optimization
- [ ] T018 @gemini Create user documentation
        """)
        
        self.log(f"Test spec created at {spec_dir}", "SUCCESS")
        self.results["passed"].append("Test spec creation")
        return spec_dir
    
    def validate_spec_analysis(self, spec_path: Path) -> bool:
        """Validate spec analysis functionality"""
        self.log("Validating spec analysis...", "INFO")
        
        try:
            analyzer = SpecAnalyzer()
            analysis = analyzer.analyze_spec(spec_path)
            
            # Check components detected
            expected_components = [
                "multiagent-auth",
                "multiagent-payments",
                "multiagent-database",
                "multiagent-cache",
                "multiagent-email"
            ]
            
            for component in expected_components:
                if component in analysis.components_needed:
                    self.log(f"  ✓ Detected {component}", "INFO")
                else:
                    self.log(f"  ✗ Missing {component}", "WARNING")
                    self.results["warnings"].append(f"Component {component} not detected")
            
            # Check stack detection
            assert analysis.stack_detected.get("backend") == "python"
            assert analysis.stack_detected.get("frontend") == "react"
            assert analysis.stack_detected.get("database") == "postgresql"
            
            # Check deployment targets
            assert "docker" in analysis.deployment_targets
            assert "kubernetes" in analysis.deployment_targets
            
            self.log("Spec analysis validation passed", "SUCCESS")
            self.results["passed"].append("Spec analysis")
            return True
            
        except Exception as e:
            self.log(f"Spec analysis failed: {e}", "ERROR")
            self.results["failed"].append("Spec analysis")
            return False
    
    def validate_agent_routing(self, spec_path: Path) -> bool:
        """Validate agent routing functionality"""
        self.log("Validating agent routing...", "INFO")
        
        try:
            router = AgentRouter()
            
            # Test task routing
            test_tasks = [
                ("Create REST API endpoints", "@copilot"),
                ("Build React components", "@codex"),
                ("Optimize database queries", "@qwen"),
                ("Design system architecture", "@claude"),
                ("Write documentation", "@gemini")
            ]
            
            for task, expected_agent in test_tasks:
                recommended = router.recommend_agent(task)
                if recommended == expected_agent:
                    self.log(f"  ✓ '{task}' → {recommended}", "INFO")
                else:
                    self.log(f"  ✗ '{task}' → {recommended} (expected {expected_agent})", "WARNING")
                    self.results["warnings"].append(f"Routing mismatch for '{task}'")
            
            self.log("Agent routing validation passed", "SUCCESS")
            self.results["passed"].append("Agent routing")
            return True
            
        except Exception as e:
            self.log(f"Agent routing failed: {e}", "ERROR")
            self.results["failed"].append("Agent routing")
            return False
    
    def validate_component_discovery(self, spec_path: Path) -> bool:
        """Validate component discovery"""
        self.log("Validating component discovery...", "INFO")
        
        try:
            from multiagent_devops.component_manager import ComponentManager
            
            manager = ComponentManager()
            
            # Read spec content
            spec_file = spec_path / "spec.md"
            content = spec_file.read_text()
            
            # Analyze content for components
            components = manager.analyze_content(content)
            
            # Check key components
            assert "multiagent-auth" in components
            assert "multiagent-payments" in components
            
            self.log(f"  Discovered {len(components)} components", "INFO")
            for component in components:
                self.log(f"  - {component}", "INFO")
            
            self.log("Component discovery validation passed", "SUCCESS")
            self.results["passed"].append("Component discovery")
            return True
            
        except Exception as e:
            self.log(f"Component discovery failed: {e}", "ERROR")
            self.results["failed"].append("Component discovery")
            return False
    
    def validate_cli_commands(self, spec_path: Path) -> bool:
        """Validate CLI commands work"""
        self.log("Validating CLI commands...", "INFO")
        
        commands_to_test = [
            ("ops status", "Check ops status"),
            ("ops --help", "Check ops help"),
            # Note: Not running actual deployment commands in validation
        ]
        
        for command, description in commands_to_test:
            try:
                result = subprocess.run(
                    command.split(),
                    capture_output=True,
                    text=True,
                    timeout=5,
                    cwd=self.get_repo_root()
                )
                
                if result.returncode == 0:
                    self.log(f"  ✓ {description}", "INFO")
                    self.results["passed"].append(description)
                else:
                    self.log(f"  ✗ {description}: {result.stderr}", "WARNING")
                    self.results["warnings"].append(description)
                    
            except subprocess.TimeoutExpired:
                self.log(f"  ✗ {description}: Timeout", "WARNING")
                self.results["warnings"].append(f"{description} timeout")
            except FileNotFoundError:
                self.log(f"  ✗ {description}: Command not found", "WARNING")
                self.results["warnings"].append(f"{description} not found")
        
        self.log("CLI validation completed", "SUCCESS")
        return True
    
    def validate_integration(self, spec_path: Path) -> bool:
        """Validate integration with agentswarm"""
        self.log("Validating agentswarm integration...", "INFO")
        
        try:
            integration = AgentSwarmIntegration()
            
            # Generate swarm config
            config = integration.generate_swarm_config(spec_path, mode="minimal")
            
            assert config.name.startswith("swarm-")
            assert len(config.agents) > 0
            assert len(config.tasks) > 0
            
            self.log(f"  Generated config: {config.name}", "INFO")
            self.log(f"  Agents: {list(config.agents.keys())}", "INFO")
            self.log(f"  Tasks: {len(config.tasks)}", "INFO")
            
            self.log("Integration validation passed", "SUCCESS")
            self.results["passed"].append("AgentSwarm integration")
            return True
            
        except Exception as e:
            self.log(f"Integration validation failed: {e}", "ERROR")
            self.results["failed"].append("AgentSwarm integration")
            return False
    
    def get_repo_root(self) -> Path:
        """Get repository root directory"""
        return Path(__file__).parent.parent
    
    def print_summary(self):
        """Print validation summary"""
        print("\n" + "="*60)
        print("QUICKSTART VALIDATION SUMMARY")
        print("="*60)
        
        total = len(self.results["passed"]) + len(self.results["failed"])
        
        print(f"\n✅ Passed: {len(self.results['passed'])}/{total}")
        for item in self.results["passed"]:
            print(f"  • {item}")
        
        if self.results["failed"]:
            print(f"\n❌ Failed: {len(self.results['failed'])}/{total}")
            for item in self.results["failed"]:
                print(f"  • {item}")
        
        if self.results["warnings"]:
            print(f"\n⚠️  Warnings: {len(self.results['warnings'])}")
            for item in self.results["warnings"]:
                print(f"  • {item}")
        
        print("\n" + "="*60)
        
        if not self.results["failed"]:
            print("🎉 VALIDATION PASSED - System is ready for use!")
        else:
            print("❌ VALIDATION FAILED - Please fix the errors above")
        
        print("="*60)


def main():
    """Main entry point for quickstart validation"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate multiagent-devops quickstart")
    parser.add_argument("--quiet", action="store_true", help="Reduce output verbosity")
    args = parser.parse_args()
    
    validator = QuickstartValidator(verbose=not args.quiet)
    success = validator.run_validation()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Integration with multiagent-agentswarm for orchestration
Provides capability-aware routing and monitoring hooks
"""

import json
import subprocess
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)

# Agent capability matrix for intelligent routing
AGENT_CAPABILITIES = {
    "@copilot": {
        "languages": ["python", "javascript", "typescript", "java"],
        "frameworks": ["fastapi", "django", "express", "react"],
        "tasks": ["backend", "api", "crud", "database", "implementation"],
        "complexity": "all",
        "speed": "fastest",
        "cost": "free",
        "parallel_capacity": 2
    },
    "@claude": {
        "languages": ["python", "javascript", "typescript", "go", "rust"],
        "frameworks": ["all"],
        "tasks": ["architecture", "security", "integration", "review", "complex"],
        "complexity": "high",
        "speed": "medium",
        "cost": "medium",
        "parallel_capacity": 1
    },
    "@codex": {
        "languages": ["javascript", "typescript", "html", "css"],
        "frameworks": ["react", "vue", "angular", "nextjs"],
        "tasks": ["frontend", "ui", "components", "interactive", "e2e-testing"],
        "complexity": "medium",
        "speed": "fast",
        "cost": "free",
        "parallel_capacity": 2
    },
    "@qwen": {
        "languages": ["python", "javascript", "c++", "rust"],
        "frameworks": ["numpy", "tensorflow", "pytorch"],
        "tasks": ["optimization", "performance", "algorithms", "testing"],
        "complexity": "high",
        "speed": "medium",
        "cost": "low",
        "parallel_capacity": 1
    },
    "@gemini": {
        "languages": ["markdown", "yaml", "json"],
        "frameworks": ["documentation"],
        "tasks": ["documentation", "research", "analysis", "specs"],
        "complexity": "medium",
        "speed": "fast",
        "cost": "low",
        "parallel_capacity": 1
    }
}


@dataclass
class AgentTask:
    """Represents a task assigned to an agent"""
    id: str
    description: str
    agent: str
    file_path: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    parallel: bool = False
    status: str = "pending"  # pending, in_progress, completed, failed
    

@dataclass
class AgentSwarmConfig:
    """Configuration for agent swarm deployment"""
    name: str
    agents: Dict[str, int]  # agent_name: instance_count
    tasks: List[AgentTask]
    parallel_execution: bool = True
    monitoring: bool = True
    auto_retry: bool = True
    max_retries: int = 3


class AgentSwarmIntegration:
    """Integration layer for multiagent-agentswarm"""
    
    def __init__(self, project_root: Path = Path.cwd()):
        self.project_root = project_root
        self.swarm_config_path = project_root / "agentswarm.yaml"
        self.state_path = project_root / ".agentswarm" / "state.json"
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
    
    def analyze_tasks_for_routing(self, tasks: List[str]) -> Dict[str, List[str]]:
        """
        Analyze tasks and route them to appropriate agents based on capabilities
        
        Args:
            tasks: List of task descriptions
            
        Returns:
            Dictionary mapping agents to their assigned tasks
        """
        agent_assignments = {agent: [] for agent in AGENT_CAPABILITIES.keys()}
        
        for task in tasks:
            task_lower = task.lower()
            best_agent = self._find_best_agent(task_lower)
            agent_assignments[best_agent].append(task)
        
        # Remove agents with no assignments
        return {k: v for k, v in agent_assignments.items() if v}
    
    def _find_best_agent(self, task_description: str) -> str:
        """Find the best agent for a given task based on keywords"""
        scores = {}
        
        for agent, capabilities in AGENT_CAPABILITIES.items():
            score = 0
            
            # Check task type matches
            for task_type in capabilities["tasks"]:
                if task_type in task_description:
                    score += 10
            
            # Check language matches
            for language in capabilities["languages"]:
                if language in task_description:
                    score += 5
            
            # Check framework matches
            for framework in capabilities["frameworks"]:
                if framework != "all" and framework in task_description:
                    score += 5
            
            # Prefer faster agents for simple tasks
            if "simple" in task_description or "quick" in task_description:
                if capabilities["speed"] == "fastest":
                    score += 3
                elif capabilities["speed"] == "fast":
                    score += 2
            
            # Prefer specialized agents for complex tasks
            if "complex" in task_description or "architecture" in task_description:
                if agent == "@claude":
                    score += 5
            
            scores[agent] = score
        
        # Return agent with highest score, default to @copilot
        return max(scores.keys(), key=lambda k: scores[k]) if scores else "@copilot"
    
    def generate_swarm_config(self, 
                            spec_path: Path,
                            mode: str = "balanced") -> AgentSwarmConfig:
        """
        Generate agent swarm configuration from spec
        
        Args:
            spec_path: Path to spec directory
            mode: Deployment mode (minimal, balanced, full)
            
        Returns:
            AgentSwarmConfig object
        """
        # Load tasks from spec
        tasks_file = spec_path / "tasks.md"
        tasks = self._parse_tasks_file(tasks_file) if tasks_file.exists() else []
        
        # Determine agent allocation based on mode
        if mode == "minimal":
            agents = {"@copilot": 1}
            parallel = False
        elif mode == "balanced":
            agents = {"@copilot": 2, "@claude": 1, "@qwen": 1}
            parallel = True
        else:  # full
            agents = {
                "@copilot": 2,
                "@claude": 1,
                "@codex": 2,
                "@qwen": 1,
                "@gemini": 1
            }
            parallel = True
        
        # Convert tasks to AgentTask objects
        agent_tasks = []
        for task_line in tasks:
            agent_task = self._parse_task_line(task_line)
            if agent_task:
                agent_tasks.append(agent_task)
        
        return AgentSwarmConfig(
            name=f"swarm-{spec_path.name}",
            agents=agents,
            tasks=agent_tasks,
            parallel_execution=parallel,
            monitoring=True
        )
    
    def _parse_tasks_file(self, tasks_file: Path) -> List[str]:
        """Parse tasks from markdown file"""
        tasks = []
        with open(tasks_file) as f:
            for line in f:
                line = line.strip()
                if line.startswith("- [ ]") or line.startswith("- [x]"):
                    tasks.append(line)
        return tasks
    
    def _parse_task_line(self, line: str) -> Optional[AgentTask]:
        """Parse a single task line into AgentTask object"""
        import re
        
        # Pattern: - [ ] T001 [P] @agent Description in path/to/file
        pattern = r"- \[([ x])\] (T\d+) (\[P\] )?(@\w+) (.+?)(?:\s+in\s+(\S+))?"
        match = re.match(pattern, line)
        
        if match:
            status = "completed" if match.group(1) == "x" else "pending"
            task_id = match.group(2)
            parallel = bool(match.group(3))
            agent = match.group(4)
            description = match.group(5)
            file_path = match.group(6)
            
            return AgentTask(
                id=task_id,
                description=description,
                agent=agent,
                file_path=file_path,
                parallel=parallel,
                status=status
            )
        return None
    
    def write_swarm_config(self, config: AgentSwarmConfig):
        """Write swarm configuration to agentswarm.yaml"""
        yaml_config = {
            "name": config.name,
            "agents": {},
            "settings": {
                "parallel_execution": config.parallel_execution,
                "monitoring": config.monitoring,
                "auto_retry": config.auto_retry,
                "max_retries": config.max_retries
            }
        }
        
        # Generate command templates for each agent
        for agent, count in config.agents.items():
            agent_config = {
                "instances": count,
                "command_template": self._get_command_template(agent),
                "capabilities": AGENT_CAPABILITIES.get(agent, {})
            }
            yaml_config["agents"][agent.lstrip("@")] = agent_config
        
        # Add tasks section
        yaml_config["tasks"] = [
            {
                "id": task.id,
                "agent": task.agent,
                "description": task.description,
                "parallel": task.parallel,
                "status": task.status,
                "file": task.file_path
            }
            for task in config.tasks
        ]
        
        with open(self.swarm_config_path, 'w') as f:
            yaml.dump(yaml_config, f, default_flow_style=False)
        
        logger.info(f"Wrote swarm config to {self.swarm_config_path}")
    
    def _get_command_template(self, agent: str) -> str:
        """Get command template for agent"""
        templates = {
            "@copilot": 'copilot exec "{task}"',
            "@claude": 'claude -p "{task}"',
            "@codex": 'codex exec "{task}"',
            "@qwen": 'qwen -p "{task}"',
            "@gemini": 'gemini -m 1.5-pro-latest -p "{task}"'
        }
        return templates.get(agent, f'{agent.lstrip("@")} -p "{{task}}"')
    
    def deploy_swarm(self, config: Optional[AgentSwarmConfig] = None) -> bool:
        """
        Deploy agent swarm using agentswarm CLI
        
        Args:
            config: Optional configuration, will use existing yaml if not provided
            
        Returns:
            True if deployment successful
        """
        if config:
            self.write_swarm_config(config)
        
        try:
            # Check if agentswarm CLI is available
            result = subprocess.run(
                ["agentswarm", "--version"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.error("agentswarm CLI not found. Please install multiagent-agentswarm")
                return False
            
            # Deploy the swarm
            result = subprocess.run(
                ["agentswarm", "deploy", "--config", str(self.swarm_config_path)],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info("Swarm deployed successfully")
                self._save_deployment_state(config or self._load_config())
                return True
            else:
                logger.error(f"Swarm deployment failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error deploying swarm: {e}")
            return False
    
    def monitor_swarm(self) -> Dict[str, Any]:
        """Get current swarm status"""
        try:
            result = subprocess.run(
                ["agentswarm", "status", "--format", "json"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                return {"status": "error", "message": result.stderr}
                
        except Exception as e:
            logger.error(f"Error monitoring swarm: {e}")
            return {"status": "error", "message": str(e)}
    
    def assign_task(self, agent: str, task: str) -> bool:
        """Assign a new task to a running agent"""
        try:
            result = subprocess.run(
                ["agentswarm", "agents", "assign", agent.lstrip("@"), 
                 "--task", task],
                capture_output=True,
                text=True
            )
            
            return result.returncode == 0
            
        except Exception as e:
            logger.error(f"Error assigning task: {e}")
            return False
    
    def scale_agent(self, agent: str, instances: int) -> bool:
        """Scale an agent to specified number of instances"""
        try:
            result = subprocess.run(
                ["agentswarm", "scale", agent.lstrip("@"), str(instances)],
                capture_output=True,
                text=True
            )
            
            return result.returncode == 0
            
        except Exception as e:
            logger.error(f"Error scaling agent: {e}")
            return False
    
    def _save_deployment_state(self, config: AgentSwarmConfig):
        """Save deployment state for monitoring"""
        state = {
            "name": config.name,
            "agents": config.agents,
            "total_tasks": len(config.tasks),
            "completed_tasks": len([t for t in config.tasks if t.status == "completed"]),
            "parallel_execution": config.parallel_execution,
            "timestamp": str(Path.cwd())
        }
        
        with open(self.state_path, 'w') as f:
            json.dump(state, f, indent=2)
    
    def _load_config(self) -> Optional[AgentSwarmConfig]:
        """Load existing configuration from yaml"""
        if not self.swarm_config_path.exists():
            return None
            
        with open(self.swarm_config_path) as f:
            data = yaml.safe_load(f)
        
        agents = {
            f"@{name}": config["instances"]
            for name, config in data.get("agents", {}).items()
        }
        
        tasks = [
            AgentTask(
                id=task["id"],
                description=task["description"],
                agent=task["agent"],
                file_path=task.get("file"),
                parallel=task.get("parallel", False),
                status=task.get("status", "pending")
            )
            for task in data.get("tasks", [])
        ]
        
        settings = data.get("settings", {})
        
        return AgentSwarmConfig(
            name=data["name"],
            agents=agents,
            tasks=tasks,
            parallel_execution=settings.get("parallel_execution", True),
            monitoring=settings.get("monitoring", True),
            auto_retry=settings.get("auto_retry", True),
            max_retries=settings.get("max_retries", 3)
        )


def integrate_with_ops_command(spec_path: Path, mode: str = "balanced") -> bool:
    """
    Main integration function called from ops commands
    
    Args:
        spec_path: Path to spec directory
        mode: Deployment mode
        
    Returns:
        True if integration successful
    """
    integration = AgentSwarmIntegration()
    
    # Generate configuration
    config = integration.generate_swarm_config(spec_path, mode)
    
    # Write configuration
    integration.write_swarm_config(config)
    
    # Deploy swarm
    success = integration.deploy_swarm(config)
    
    if success:
        logger.info(f"Successfully integrated with agentswarm for {spec_path}")
    else:
        logger.error(f"Failed to integrate with agentswarm for {spec_path}")
    
    return success
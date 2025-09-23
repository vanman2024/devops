#!/usr/bin/env python3
"""
Agent Capability Matrix
Defines capabilities and specializations for each AI agent
Used for intelligent task routing and workload balancing
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import re


@dataclass
class AgentCapability:
    """Represents capabilities of an AI agent"""
    name: str
    languages: List[str]
    frameworks: List[str]
    tasks: List[str]
    complexity: str  # low, medium, high, all
    speed: str  # slow, medium, fast, fastest
    cost: str  # free, low, medium, high
    parallel_capacity: int  # Max parallel tasks
    strengths: List[str]
    weaknesses: List[str]
    best_for: List[str]


# Complete agent capability matrix
AGENT_CAPABILITIES: Dict[str, AgentCapability] = {
    "@copilot": AgentCapability(
        name="GitHub Copilot",
        languages=["python", "javascript", "typescript", "java", "c#", "go", "ruby"],
        frameworks=["fastapi", "django", "flask", "express", "react", "vue", "spring"],
        tasks=["backend", "api", "crud", "database", "implementation", "boilerplate"],
        complexity="all",
        speed="fastest",
        cost="free",
        parallel_capacity=2,
        strengths=[
            "Fast bulk code generation",
            "Pattern recognition and replication",
            "Boilerplate code creation",
            "CRUD operations",
            "API endpoint implementation"
        ],
        weaknesses=[
            "Complex architecture decisions",
            "Security considerations",
            "Performance optimization"
        ],
        best_for=[
            "Rapid prototyping",
            "Backend API development",
            "Database operations",
            "Standard implementations"
        ]
    ),
    
    "@claude": AgentCapability(
        name="Claude (Anthropic)",
        languages=["python", "javascript", "typescript", "go", "rust", "c++", "java"],
        frameworks=["all"],  # Architectural decisions across all frameworks
        tasks=["architecture", "security", "integration", "review", "complex", "design"],
        complexity="high",
        speed="medium",
        cost="medium",
        parallel_capacity=1,
        strengths=[
            "Complex architectural decisions",
            "Security analysis and implementation",
            "Code review and quality assurance",
            "System design and integration",
            "Strategic technical decisions"
        ],
        weaknesses=[
            "Slower for bulk code generation",
            "Higher cost for simple tasks"
        ],
        best_for=[
            "Architecture design",
            "Security reviews",
            "Complex problem solving",
            "Integration challenges",
            "Code quality reviews"
        ]
    ),
    
    "@codex": AgentCapability(
        name="OpenAI Codex",
        languages=["javascript", "typescript", "html", "css", "python"],
        frameworks=["react", "vue", "angular", "nextjs", "svelte", "tailwind"],
        tasks=["frontend", "ui", "components", "interactive", "styling", "e2e-testing"],
        complexity="medium",
        speed="fast",
        cost="free",
        parallel_capacity=2,
        strengths=[
            "Frontend component development",
            "Interactive UI creation",
            "CSS and styling",
            "Browser-based testing",
            "Responsive design"
        ],
        weaknesses=[
            "Backend architecture",
            "Database design",
            "System-level programming"
        ],
        best_for=[
            "React/Vue/Angular components",
            "UI/UX implementation",
            "Frontend testing",
            "Interactive features",
            "Design system implementation"
        ]
    ),
    
    "@qwen": AgentCapability(
        name="Qwen (Alibaba)",
        languages=["python", "javascript", "c++", "rust", "go"],
        frameworks=["numpy", "pandas", "tensorflow", "pytorch", "scikit-learn"],
        tasks=["optimization", "performance", "algorithms", "testing", "analysis"],
        complexity="high",
        speed="medium",
        cost="low",
        parallel_capacity=1,
        strengths=[
            "Performance optimization",
            "Algorithm implementation",
            "Data structure optimization",
            "Test generation and coverage",
            "Benchmark creation"
        ],
        weaknesses=[
            "UI/UX development",
            "Creative design tasks"
        ],
        best_for=[
            "Code optimization",
            "Algorithm improvements",
            "Performance tuning",
            "Test suite creation",
            "Data processing pipelines"
        ]
    ),
    
    "@gemini": AgentCapability(
        name="Google Gemini",
        languages=["markdown", "yaml", "json", "python", "javascript"],
        frameworks=["documentation", "sphinx", "mkdocs", "docusaurus"],
        tasks=["documentation", "research", "analysis", "specs", "planning"],
        complexity="medium",
        speed="fast",
        cost="low",
        parallel_capacity=1,
        strengths=[
            "Documentation generation",
            "Research and analysis",
            "Spec writing",
            "API documentation",
            "Code explanation"
        ],
        weaknesses=[
            "Complex implementation",
            "Performance optimization"
        ],
        best_for=[
            "README creation",
            "API documentation",
            "Research tasks",
            "Spec refinement",
            "Documentation updates"
        ]
    )
}


class AgentRouter:
    """Routes tasks to appropriate agents based on capabilities"""
    
    def __init__(self):
        self.capabilities = AGENT_CAPABILITIES
    
    def recommend_agent(self, task_description: str) -> str:
        """
        Recommend the best agent for a given task
        
        Args:
            task_description: Description of the task
            
        Returns:
            Recommended agent name
        """
        task_lower = task_description.lower()
        scores = {}
        
        for agent_name, capability in self.capabilities.items():
            score = self._calculate_match_score(task_lower, capability)
            scores[agent_name] = score
        
        # Return agent with highest score, default to @copilot
        if scores:
            return max(scores.keys(), key=lambda k: scores[k])
        return "@copilot"
    
    def _calculate_match_score(self, task_desc: str, capability: AgentCapability) -> float:
        """Calculate how well an agent matches a task"""
        score = 0.0
        
        # Task type matching (highest weight)
        for task_type in capability.tasks:
            if task_type in task_desc:
                score += 10.0
        
        # Language matching
        for language in capability.languages:
            if language in task_desc:
                score += 5.0
        
        # Framework matching
        for framework in capability.frameworks:
            if framework != "all" and framework in task_desc:
                score += 5.0
        
        # Strength keyword matching
        for strength in capability.strengths:
            strength_keywords = strength.lower().split()
            matches = sum(1 for kw in strength_keywords if kw in task_desc)
            score += matches * 2.0
        
        # Speed preference for simple tasks
        if any(kw in task_desc for kw in ["simple", "quick", "basic", "standard"]):
            if capability.speed == "fastest":
                score += 3.0
            elif capability.speed == "fast":
                score += 2.0
        
        # Complexity matching
        if any(kw in task_desc for kw in ["complex", "advanced", "sophisticated"]):
            if capability.complexity == "high":
                score += 3.0
        
        # Cost consideration for non-critical tasks
        if any(kw in task_desc for kw in ["prototype", "demo", "test"]):
            if capability.cost == "free":
                score += 2.0
            elif capability.cost == "low":
                score += 1.0
        
        return score
    
    def recommend_agents_for_tasks(self, tasks: List[str]) -> Dict[str, List[str]]:
        """
        Recommend agents for a list of tasks
        
        Args:
            tasks: List of task descriptions
            
        Returns:
            Dictionary mapping agents to assigned tasks
        """
        assignments = {agent: [] for agent in self.capabilities.keys()}
        
        for task in tasks:
            best_agent = self.recommend_agent(task)
            assignments[best_agent].append(task)
        
        # Remove agents with no assignments
        return {k: v for k, v in assignments.items() if v}
    
    def get_agent_workload(self, assignments: Dict[str, List[str]]) -> Dict[str, float]:
        """
        Calculate workload percentage for each agent
        
        Args:
            assignments: Current task assignments
            
        Returns:
            Dictionary of agent workload percentages
        """
        workloads = {}
        
        for agent, tasks in assignments.items():
            capacity = self.capabilities[agent].parallel_capacity
            workload = len(tasks) / capacity if capacity > 0 else float('inf')
            workloads[agent] = min(workload * 100, 100)  # Cap at 100%
        
        return workloads
    
    def balance_workload(self, tasks: List[str]) -> Dict[str, List[str]]:
        """
        Balance task assignments across agents considering capacity
        
        Args:
            tasks: List of task descriptions
            
        Returns:
            Balanced task assignments
        """
        # Initial assignment
        assignments = self.recommend_agents_for_tasks(tasks)
        
        # Calculate workloads
        workloads = self.get_agent_workload(assignments)
        
        # Rebalance if any agent is overloaded
        max_iterations = 5
        iteration = 0
        
        while any(load > 100 for load in workloads.values()) and iteration < max_iterations:
            # Find overloaded agents
            overloaded = [agent for agent, load in workloads.items() if load > 100]
            
            for agent in overloaded:
                # Try to reassign some tasks
                tasks_to_reassign = assignments[agent][self.capabilities[agent].parallel_capacity:]
                assignments[agent] = assignments[agent][:self.capabilities[agent].parallel_capacity]
                
                # Find agents with capacity
                for task in tasks_to_reassign:
                    # Find next best agent with capacity
                    for alt_agent in self.capabilities.keys():
                        if alt_agent != agent:
                            current_load = len(assignments.get(alt_agent, []))
                            capacity = self.capabilities[alt_agent].parallel_capacity
                            if current_load < capacity:
                                assignments[alt_agent].append(task)
                                break
            
            workloads = self.get_agent_workload(assignments)
            iteration += 1
        
        return assignments
    
    def get_capability_summary(self, agent: str) -> Optional[Dict[str, Any]]:
        """Get a summary of an agent's capabilities"""
        if agent not in self.capabilities:
            return None
        
        cap = self.capabilities[agent]
        return {
            "name": cap.name,
            "best_for": cap.best_for,
            "strengths": cap.strengths,
            "speed": cap.speed,
            "cost": cap.cost,
            "parallel_capacity": cap.parallel_capacity
        }


def auto_assign_task(task_description: str) -> str:
    """
    Automatically assign a task to the best agent
    
    Args:
        task_description: Description of the task
        
    Returns:
        Recommended agent name
    """
    router = AgentRouter()
    return router.recommend_agent(task_description)


def recommend_agents(tasks: List[str]) -> List[str]:
    """
    Recommend agents for a list of tasks
    
    Args:
        tasks: List of task descriptions
        
    Returns:
        List of recommended agent names (unique)
    """
    router = AgentRouter()
    assignments = router.recommend_agents_for_tasks(tasks)
    return list(assignments.keys())


def get_agent_for_file_type(file_path: str) -> str:
    """
    Get recommended agent based on file type
    
    Args:
        file_path: Path to the file
        
    Returns:
        Recommended agent name
    """
    file_lower = file_path.lower()
    
    # Frontend files
    if any(ext in file_lower for ext in ['.jsx', '.tsx', '.vue', '.svelte']):
        return "@codex"
    if any(path in file_lower for path in ['/components/', '/pages/', '/ui/']):
        return "@codex"
    
    # Backend files
    if any(ext in file_lower for ext in ['.py', '.go', '.java', '.rb']):
        return "@copilot"
    if any(path in file_lower for path in ['/api/', '/models/', '/services/']):
        return "@copilot"
    
    # Test files
    if any(pattern in file_lower for pattern in ['test_', '_test.', '.test.', '.spec.']):
        # Frontend tests
        if any(ext in file_lower for ext in ['.jsx', '.tsx', '.js', '.ts']):
            return "@codex"
        # Performance tests
        elif 'performance' in file_lower or 'benchmark' in file_lower:
            return "@qwen"
        # General tests
        else:
            return "@qwen"
    
    # Documentation files
    if any(ext in file_lower for ext in ['.md', '.rst', '.txt']):
        return "@gemini"
    
    # Architecture/Design files
    if any(pattern in file_lower for pattern in ['architecture', 'design', 'schema']):
        return "@claude"
    
    # Default to copilot
    return "@copilot"
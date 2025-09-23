"""
AgentSwarm model: Group of AI agents working in parallel on tasks
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, validator
from enum import Enum
from datetime import datetime
from .task import Task


class SwarmStatus(str, Enum):
    """Agent swarm status enumeration"""
    DEPLOYED = "deployed"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class LogEntry:
    """Log entry for swarm activities"""
    timestamp: datetime
    agent: str
    task_id: Optional[str]
    message: str
    level: str = "info"  # info, warning, error


class AgentSwarm(BaseModel):
    """
    Represents a group of AI agents working in parallel on tasks.

    An AgentSwarm coordinates multiple agents working on related tasks,
    tracking progress and maintaining logs of activities.
    """

    id: str = Field(..., description="Unique swarm identifier")
    agents: List[str] = Field(..., description="List of agent names in the swarm")
    tasks: List[Task] = Field(default_factory=list, description="Tasks assigned to the swarm")
    status: SwarmStatus = Field(default=SwarmStatus.DEPLOYED, description="Swarm status")
    logs: List[LogEntry] = Field(default_factory=list, description="Activity logs")
    created_at: datetime = Field(default_factory=datetime.now, description="Swarm creation time")
    completed_at: Optional[datetime] = Field(default=None, description="Swarm completion time")

    @validator('agents')
    def validate_agents(cls, v):
        """Ensure agents list is non-empty"""
        if not v:
            raise ValueError('Agents list must be non-empty')
        return v

    @validator('id')
    def validate_id(cls, v):
        """Validate swarm ID format"""
        import re
        if not re.match(r'^swarm-\d{8}-\w+$', v):
            raise ValueError('Swarm ID must match pattern swarm-YYYYMMDD-identifier')
        return v

    def add_task(self, task: Task) -> None:
        """Add a task to the swarm"""
        if task.assigned_agent not in self.agents:
            raise ValueError(f"Task assigned to agent {task.assigned_agent} not in swarm")
        self.tasks.append(task)
        self.log_activity(task.assigned_agent, task.id, f"Task {task.id} added to swarm")

    def get_tasks_for_agent(self, agent: str) -> List[Task]:
        """Get all tasks assigned to a specific agent"""
        return [task for task in self.tasks if task.assigned_agent == agent]

    def get_pending_tasks(self) -> List[Task]:
        """Get all pending tasks in the swarm"""
        return [task for task in self.tasks if task.is_pending()]

    def get_in_progress_tasks(self) -> List[Task]:
        """Get all in-progress tasks in the swarm"""
        return [task for task in self.tasks if task.is_in_progress()]

    def get_completed_tasks(self) -> List[Task]:
        """Get all completed tasks in the swarm"""
        return [task for task in self.tasks if task.is_completed()]

    def start_task(self, task_id: str) -> None:
        """Mark a task as in progress"""
        task = self._get_task_by_id(task_id)
        task.mark_in_progress()
        self.log_activity(task.assigned_agent, task_id, f"Task {task_id} started")
        self._update_status()

    def complete_task(self, task_id: str) -> None:
        """Mark a task as completed"""
        task = self._get_task_by_id(task_id)
        task.mark_completed()
        self.log_activity(task.assigned_agent, task_id, f"Task {task_id} completed")
        self._update_status()

    def log_activity(self, agent: str, task_id: Optional[str], message: str, level: str = "info") -> None:
        """Add a log entry for swarm activity"""
        entry = LogEntry(
            timestamp=datetime.now(),
            agent=agent,
            task_id=task_id,
            message=message,
            level=level
        )
        self.logs.append(entry)

    def get_logs_for_agent(self, agent: str) -> List[LogEntry]:
        """Get all log entries for a specific agent"""
        return [log for log in self.logs if log.agent == agent]

    def get_logs_for_task(self, task_id: str) -> List[LogEntry]:
        """Get all log entries for a specific task"""
        return [log for log in self.logs if log.task_id == task_id]

    def is_running(self) -> bool:
        """Check if swarm is currently running"""
        return self.status == SwarmStatus.RUNNING

    def is_completed(self) -> bool:
        """Check if swarm has completed all tasks"""
        return self.status == SwarmStatus.COMPLETED

    def get_progress_percentage(self) -> float:
        """Get completion percentage of tasks"""
        if not self.tasks:
            return 100.0
        completed = len(self.get_completed_tasks())
        return (completed / len(self.tasks)) * 100

    def _get_task_by_id(self, task_id: str) -> Task:
        """Get task by ID"""
        for task in self.tasks:
            if task.id == task_id:
                return task
        raise ValueError(f"Task {task_id} not found in swarm")

    def _update_status(self) -> None:
        """Update swarm status based on task completion"""
        if self.status == SwarmStatus.DEPLOYED and self.get_in_progress_tasks():
            self.status = SwarmStatus.RUNNING
        elif self.status == SwarmStatus.RUNNING and not self.get_pending_tasks() and not self.get_in_progress_tasks():
            self.status = SwarmStatus.COMPLETED
            self.completed_at = datetime.now()

    @classmethod
    def create_for_spec(cls, spec_id: str, agents: List[str]) -> 'AgentSwarm':
        """
        Create a new swarm for a spec with the given agents.

        Args:
            spec_id: Spec identifier
            agents: List of agent names

        Returns:
            New AgentSwarm instance
        """
        from datetime import datetime
        swarm_id = f"swarm-{datetime.now().strftime('%Y%m%d')}-{spec_id}"

        swarm = cls(
            id=swarm_id,
            agents=agents
        )

        swarm.log_activity("system", None, f"Swarm created for spec {spec_id} with agents {', '.join(agents)}")
        return swarm

    class Config:
        """Pydantic configuration"""
        use_enum_values = True
        validate_assignment = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            LogEntry: lambda v: {
                "timestamp": v.timestamp.isoformat(),
                "agent": v.agent,
                "task_id": v.task_id,
                "message": v.message,
                "level": v.level
            }
        }
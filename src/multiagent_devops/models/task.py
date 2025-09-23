"""
Task model: Individual actionable items assigned to agents
"""

from dataclasses import dataclass, field
from typing import List, Optional
from pydantic import BaseModel, Field, validator
from enum import Enum


class TaskStatus(str, Enum):
    """Task status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class Task(BaseModel):
    """
    Represents an individual actionable item from tasks.md.

    Tasks are assigned to specific agents and have dependencies
    that must be completed before they can be started.
    """

    id: str = Field(..., description="Task ID (T001, T002, etc.)")
    description: str = Field(..., description="Task description")
    assigned_agent: str = Field(..., description="Assigned agent (@copilot, @claude, etc.)")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Task status")
    dependencies: List[str] = Field(default_factory=list, description="List of task IDs this task depends on")

    @validator('id')
    def validate_id(cls, v):
        """Validate task ID format"""
        import re
        if not re.match(r'^T\d{3}$', v):
            raise ValueError('Task ID must match pattern T###')
        return v

    @validator('assigned_agent')
    def validate_assigned_agent(cls, v):
        """Validate assigned agent format"""
        import re
        if not re.match(r'^@\w+$', v):
            raise ValueError('Assigned agent must match pattern @agentname')
        return v

    @validator('dependencies')
    def validate_dependencies(cls, v):
        """Validate dependency task IDs"""
        import re
        for dep in v:
            if not re.match(r'^T\d{3}$', dep):
                raise ValueError(f'Invalid dependency task ID: {dep}')
        return v

    def can_start(self, completed_task_ids: List[str]) -> bool:
        """
        Check if this task can be started based on completed dependencies.

        Args:
            completed_task_ids: List of completed task IDs

        Returns:
            True if all dependencies are completed
        """
        return all(dep in completed_task_ids for dep in self.dependencies)

    def mark_in_progress(self) -> None:
        """Mark task as in progress"""
        if self.status != TaskStatus.PENDING:
            raise ValueError(f"Cannot start task {self.id} with status {self.status}")
        self.status = TaskStatus.IN_PROGRESS

    def mark_completed(self) -> None:
        """Mark task as completed"""
        if self.status != TaskStatus.IN_PROGRESS:
            raise ValueError(f"Cannot complete task {self.id} with status {self.status}")
        self.status = TaskStatus.COMPLETED

    def is_pending(self) -> bool:
        """Check if task is pending"""
        return self.status == TaskStatus.PENDING

    def is_in_progress(self) -> bool:
        """Check if task is in progress"""
        return self.status == TaskStatus.IN_PROGRESS

    def is_completed(self) -> bool:
        """Check if task is completed"""
        return self.status == TaskStatus.COMPLETED

    @classmethod
    def from_task_string(cls, task_string: str) -> 'Task':
        """
        Parse a task string from tasks.md and create a Task instance.

        Expected format: "- [ ] T001 @agent Description"

        Args:
            task_string: Task string from tasks.md

        Returns:
            Task instance

        Raises:
            ValueError: If task string format is invalid
        """
        import re

        # Match pattern: - [ ] T001 @agent Description
        pattern = r'-\s+\[\s*\]\s+(T\d{3})\s+(@\w+)\s+(.+)'
        match = re.match(pattern, task_string.strip())

        if not match:
            raise ValueError(f"Invalid task string format: {task_string}")

        task_id, agent, description = match.groups()

        return cls(
            id=task_id,
            description=description.strip(),
            assigned_agent=agent
        )

    def to_task_string(self) -> str:
        """Convert task back to string format for tasks.md"""
        status_marker = "x" if self.is_completed() else " "
        return f"- [{status_marker}] {self.id} {self.assigned_agent} {self.description}"

    class Config:
        """Pydantic configuration"""
        use_enum_values = True
        validate_assignment = True
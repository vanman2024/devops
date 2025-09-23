"""
Spec model: Represents feature specifications parsed from spec-kit specs
"""

from dataclasses import dataclass, field
from typing import List, Optional
from pydantic import BaseModel, Field, validator
from .task import Task


class Spec(BaseModel):
    """
    Represents a feature specification from spec-kit.

    A Spec contains the parsed information from a spec.md file and
    associated tasks.md, representing a complete feature specification.
    """

    id: str = Field(..., description="Spec directory name (e.g., '001-user-auth')")
    title: str = Field(..., description="Feature name")
    requirements: List[str] = Field(default_factory=list, description="Functional requirements")
    acceptance_criteria: List[str] = Field(default_factory=list, description="Acceptance criteria from spec.md")
    tasks: List[Task] = Field(default_factory=list, description="Associated tasks")

    @validator('id')
    def validate_id(cls, v):
        """Validate spec ID format"""
        import re
        if not re.match(r'^\d{3}-[a-z-]+$', v):
            raise ValueError('Spec ID must match pattern ###-feature-name')
        return v

    @validator('requirements')
    def validate_requirements(cls, v):
        """Ensure requirements are non-empty"""
        if not v:
            raise ValueError('Requirements must be non-empty')
        return v

    @validator('acceptance_criteria')
    def validate_acceptance_criteria(cls, v):
        """Ensure acceptance criteria are testable"""
        if not v:
            raise ValueError('Acceptance criteria must be non-empty')
        # Check that each criterion looks testable
        for criterion in v:
            if not any(keyword in criterion.lower() for keyword in ['should', 'must', 'can', 'will']):
                raise ValueError(f'Acceptance criterion must be testable: {criterion}')
        return v

    @classmethod
    def from_spec_file(cls, spec_file_path: str) -> 'Spec':
        """
        Parse a spec.md file and create a Spec instance.

        Args:
            spec_file_path: Path to the spec.md file

        Returns:
            Spec instance

        Raises:
            FileNotFoundError: If spec file doesn't exist
            ValueError: If spec file format is invalid
        """
        from pathlib import Path
        import re

        spec_path = Path(spec_file_path)
        if not spec_path.exists():
            raise FileNotFoundError(f"Spec file not found: {spec_file_path}")

        content = spec_path.read_text(encoding='utf-8')

        # Extract spec ID from directory name
        spec_dir = spec_path.parent.name
        if not re.match(r'^\d{3}-[a-z-]+$', spec_dir):
            raise ValueError(f"Invalid spec directory name: {spec_dir}")

        # Extract title (first heading)
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if not title_match:
            raise ValueError("Spec file must have a title (H1 heading)")

        title = title_match.group(1).strip()

        # Extract requirements (from ## Requirements section)
        requirements = []
        req_section = re.search(r'## Requirements\s*\n(.*?)(?=\n##|\n#|\Z)', content, re.DOTALL)
        if req_section:
            req_content = req_section.group(1)
            # Extract list items
            req_items = re.findall(r'[-*]\s+(.+)', req_content)
            requirements = [req.strip() for req in req_items if req.strip()]

        # Extract acceptance criteria (from ## Acceptance Criteria section)
        acceptance_criteria = []
        ac_section = re.search(r'## Acceptance Criteria\s*\n(.*?)(?=\n##|\n#|\Z)', content, re.DOTALL)
        if ac_section:
            ac_content = ac_section.group(1)
            # Extract list items
            ac_items = re.findall(r'[-*]\s+(.+)', ac_content)
            acceptance_criteria = [ac.strip() for ac in ac_items if ac.strip()]

        return cls(
            id=spec_dir,
            title=title,
            requirements=requirements,
            acceptance_criteria=acceptance_criteria,
            tasks=[]  # Tasks will be loaded separately
        )

    def add_task(self, task: Task) -> None:
        """Add a task to this spec"""
        self.tasks.append(task)

    def get_tasks_by_agent(self, agent: str) -> List[Task]:
        """Get all tasks assigned to a specific agent"""
        return [task for task in self.tasks if task.assigned_agent == agent]

    def get_pending_tasks(self) -> List[Task]:
        """Get all pending tasks"""
        return [task for task in self.tasks if task.status == 'pending']

    def get_completed_tasks(self) -> List[Task]:
        """Get all completed tasks"""
        return [task for task in self.tasks if task.status == 'completed']

    class Config:
        """Pydantic configuration"""
        validate_assignment = True
        json_encoders = {
            Task: lambda t: t.dict()
        }
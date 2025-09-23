"""Domain models supporting the multi-agent DevOps CLI."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class Task:
    """Represents an actionable checklist item parsed from tasks.md."""

    id: str
    description: str
    assigned_agent: str
    status: str = "pending"

    def __post_init__(self) -> None:
        if not self.id.startswith("T"):
            raise ValueError(f"Invalid task id: {self.id}")

        if not self.assigned_agent.startswith("@"):
            raise ValueError(f"Invalid agent assignment: {self.assigned_agent}")


@dataclass
class Spec:
    """Lightweight representation of a spec-kit specification."""

    id: str
    title: str
    requirements: List[str]
    acceptance_criteria: List[str]

    @classmethod
    def from_spec_file(cls, spec_file: str) -> "Spec":
        """Parse a markdown spec file and extract structured fields."""

        path = Path(spec_file)
        if not path.exists():  # pragma: no cover - defensive guard
            raise FileNotFoundError(f"Spec file not found: {spec_file}")

        title: str | None = None
        requirements: List[str] = []
        acceptance: List[str] = []
        current_section: str | None = None

        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line:
                continue

            if line.startswith("# "):
                title = line[2:].strip()
                current_section = None
                continue

            if line.startswith("## "):
                heading = line[3:].strip().lower()
                if heading.startswith("requirements"):
                    current_section = "requirements"
                elif heading.startswith("acceptance criteria"):
                    current_section = "acceptance"
                else:
                    current_section = None
                continue

            if line.startswith("- ") and current_section:
                item = line[2:].strip()
                if current_section == "requirements":
                    requirements.append(item)
                elif current_section == "acceptance":
                    acceptance.append(item)

        if not title:
            raise ValueError(f"Spec file {spec_file} missing top-level title")

        if not requirements:
            raise ValueError(f"Spec file {spec_file} missing requirements list")

        if not acceptance:
            raise ValueError(f"Spec file {spec_file} missing acceptance criteria")

        return cls(
            id=path.parent.name or title.lower().replace(" ", "-"),
            title=title,
            requirements=requirements,
            acceptance_criteria=acceptance,
        )


@dataclass
class AgentSwarm:
    """Group metadata for a deployed agent swarm."""

    id: str
    agents: List[str]
    tasks: List[Task] = field(default_factory=list)
    status: str = "deployed"


@dataclass
class DeploymentPlan:
    """Configuration persisted by `ops deploy-plan` and `ops spec-init`."""

    target: str
    environment: str
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QAReport:
    """Represents the persisted results of an `ops qa` run."""

    spec_name: str
    tests_passed: bool
    coverage_percentage: int
    security_issues: List[Dict[str, str]] = field(default_factory=list)
    performance_results: Dict[str, Any] = field(default_factory=dict)
    acceptance_criteria: List[str] = field(default_factory=list)
    acceptance_validated: bool = False
    overall_status: str = "FAIL"

    def __post_init__(self) -> None:
        if not self.spec_name:
            raise ValueError("spec_name cannot be empty")

        if not isinstance(self.tests_passed, bool):
            raise TypeError("tests_passed must be a boolean")

        if not isinstance(self.coverage_percentage, int) or not (0 <= self.coverage_percentage <= 100):
            raise ValueError("coverage_percentage must be an int between 0 and 100")

        if not isinstance(self.acceptance_validated, bool):
            raise TypeError("acceptance_validated must be a boolean")

        if self.overall_status not in {"PASS", "FAIL"}:
            raise ValueError("overall_status must be either 'PASS' or 'FAIL'")

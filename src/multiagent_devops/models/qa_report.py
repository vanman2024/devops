"""
QAReport model: Output of quality checks and validations
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime


class QAReport(BaseModel):
    """
    Output of quality checks and validations.

    Contains the results of running quality assurance checks
    on a completed spec implementation.
    """

    spec_id: str = Field(..., description="Linked spec identifier")
    tests_passed: int = Field(default=0, description="Number of tests that passed")
    tests_failed: int = Field(default=0, description="Number of tests that failed")
    security_issues: List[str] = Field(default_factory=list, description="List of security issues found")
    performance_metrics: Dict[str, Any] = Field(default_factory=dict, description="Performance metrics")
    compliance_status: bool = Field(default=False, description="Whether the implementation meets compliance requirements")
    generated_at: datetime = Field(default_factory=datetime.now, description="Report generation timestamp")
    test_coverage: Optional[float] = Field(default=None, description="Code coverage percentage")

    @validator('spec_id')
    def validate_spec_id(cls, v):
        """Validate spec ID exists"""
        import re
        if not re.match(r'^\d{3}-[a-z-]+$', v):
            raise ValueError('Spec ID must match pattern ###-feature-name')
        return v

    @validator('compliance_status')
    def validate_compliance_status(cls, v):
        """Ensure compliance status is true for deployment"""
        if not v:
            # Could add more validation here based on requirements
            pass
        return v

    @validator('test_coverage')
    def validate_test_coverage(cls, v):
        """Validate test coverage is between 0 and 100"""
        if v is not None and (v < 0 or v > 100):
            raise ValueError('Test coverage must be between 0 and 100')
        return v

    def add_security_issue(self, issue: str) -> None:
        """Add a security issue to the report"""
        self.security_issues.append(issue)

    def set_performance_metric(self, name: str, value: Any) -> None:
        """Set a performance metric"""
        self.performance_metrics[name] = value

    def get_performance_metric(self, name: str, default: Any = None) -> Any:
        """Get a performance metric value"""
        return self.performance_metrics.get(name, default)

    def calculate_success_rate(self) -> float:
        """Calculate test success rate as percentage"""
        total_tests = self.tests_passed + self.tests_failed
        if total_tests == 0:
            return 0.0
        return (self.tests_passed / total_tests) * 100

    def has_critical_issues(self) -> bool:
        """Check if report has critical issues preventing deployment"""
        # Critical issues include:
        # - Failed tests
        # - Security issues
        # - Non-compliance
        # - Low test coverage (< 80%)
        if self.tests_failed > 0:
            return True
        if self.security_issues:
            return True
        if not self.compliance_status:
            return True
        if self.test_coverage is not None and self.test_coverage < 80:
            return True
        return False

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the QA report"""
        return {
            "spec_id": self.spec_id,
            "total_tests": self.tests_passed + self.tests_failed,
            "tests_passed": self.tests_passed,
            "tests_failed": self.tests_failed,
            "success_rate": self.calculate_success_rate(),
            "security_issues_count": len(self.security_issues),
            "compliance_status": self.compliance_status,
            "test_coverage": self.test_coverage,
            "has_critical_issues": self.has_critical_issues(),
            "generated_at": self.generated_at.isoformat()
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "spec_id": self.spec_id,
            "tests_passed": self.tests_passed,
            "tests_failed": self.tests_failed,
            "security_issues": self.security_issues,
            "performance_metrics": self.performance_metrics,
            "compliance_status": self.compliance_status,
            "generated_at": self.generated_at.isoformat(),
            "test_coverage": self.test_coverage
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QAReport':
        """Create from dictionary"""
        # Handle datetime parsing
        generated_at = data.get("generated_at")
        if isinstance(generated_at, str):
            generated_at = datetime.fromisoformat(generated_at)

        return cls(
            spec_id=data["spec_id"],
            tests_passed=data.get("tests_passed", 0),
            tests_failed=data.get("tests_failed", 0),
            security_issues=data.get("security_issues", []),
            performance_metrics=data.get("performance_metrics", {}),
            compliance_status=data.get("compliance_status", False),
            generated_at=generated_at or datetime.now(),
            test_coverage=data.get("test_coverage")
        )

    @classmethod
    def create_empty_report(cls, spec_id: str) -> 'QAReport':
        """Create an empty QA report for a spec"""
        return cls(spec_id=spec_id)

    def update_from_test_results(self, passed: int, failed: int, coverage: Optional[float] = None) -> None:
        """Update report with test results"""
        self.tests_passed = passed
        self.tests_failed = failed
        if coverage is not None:
            self.test_coverage = coverage

    def mark_compliant(self) -> None:
        """Mark the implementation as compliant"""
        self.compliance_status = True

    def mark_non_compliant(self, reason: str) -> None:
        """Mark the implementation as non-compliant with reason"""
        self.compliance_status = False
        self.add_security_issue(f"Compliance failure: {reason}")

    class Config:
        """Pydantic configuration"""
        validate_assignment = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
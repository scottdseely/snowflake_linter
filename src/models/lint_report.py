"""
Data model for linting report containing results and metadata.
"""

from dataclasses import dataclass, field
from typing import List, Dict
from datetime import datetime
from .lint_result import LintResult


@dataclass
class LintReport:
    """Represents a complete linting report."""
    
    results: List[LintResult] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    total_files: int = 0
    total_violations: int = 0
    
    def __post_init__(self):
        """Update counts after initialization."""
        self.total_violations = len(self.results)
    
    def add_result(self, result: LintResult) -> None:
        """Add a result to the report."""
        self.results.append(result)
        self.total_violations = len(self.results)
    
    def add_results(self, results: List[LintResult]) -> None:
        """Add multiple results to the report."""
        self.results.extend(results)
        self.total_violations = len(self.results)
    
    def get_results_by_rule(self, rule_name: str) -> List[LintResult]:
        """Get all results for a specific rule."""
        return [r for r in self.results if r.rule == rule_name]
    
    def get_results_by_severity(self, severity: str) -> List[LintResult]:
        """Get all results for a specific severity."""
        return [r for r in self.results if r.severity == severity]
    
    def get_results_by_file(self, file_name: str) -> List[LintResult]:
        """Get all results for a specific file."""
        return [r for r in self.results if r.file == file_name]
    
    def get_summary(self) -> Dict[str, int]:
        """Get summary statistics."""
        summary = {
            'total_violations': self.total_violations,
            'total_files': self.total_files,
            'by_rule': {},
            'by_severity': {}
        }
        
        for result in self.results:
            summary['by_rule'][result.rule] = summary['by_rule'].get(result.rule, 0) + 1
            summary['by_severity'][result.severity] = summary['by_severity'].get(result.severity, 0) + 1
        
        return summary
    
    def to_dict(self) -> dict:
        """Convert report to dictionary."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'total_files': self.total_files,
            'total_violations': self.total_violations,
            'results': [r.to_dict() for r in self.results],
            'summary': self.get_summary()
        }
    
    def __str__(self) -> str:
        """Format report as string."""
        lines = [
            "LINTING REPORT",
            "=" * 60,
            f"Total violations: {self.total_violations}",
            f"Total files: {self.total_files}",
            ""
        ]
        
        if self.results:
            lines.append("Results:")
            for result in self.results:
                lines.append(f"  {result}")
        else:
            lines.append("No violations found!")
        
        return "\n".join(lines)

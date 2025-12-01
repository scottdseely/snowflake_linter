"""
Data model for a single linting result/violation.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class LintResult:
    """Represents a single linting violation."""
    
    rule: str
    severity: str
    line: int
    file: str
    message: str
    description: str
    column: Optional[int] = None
    
    def __str__(self) -> str:
        """Format result as string."""
        return f"{self.file}:{self.line} [{self.severity}] {self.rule}: {self.message}"
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'rule': self.rule,
            'severity': self.severity,
            'line': self.line,
            'file': self.file,
            'message': self.message,
            'description': self.description,
            'column': self.column
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'LintResult':
        """Create from dictionary."""
        return cls(
            rule=data['rule'],
            severity=data['severity'],
            line=data['line'],
            file=data['file'],
            message=data['message'],
            description=data['description'],
            column=data.get('column')
        )

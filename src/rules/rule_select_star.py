"""
Rule: SELECT * Detection

This rule detects all instances of SELECT * in SQL queries.
SELECT * should generally be avoided in production code as it:
- Makes code fragile to schema changes
- Includes unnecessary columns
- Can impact performance
"""

import re
from typing import List
try:
    from models.lint_result import LintResult
except ImportError:
    from ..models.lint_result import LintResult


class RuleSelectStar:
    """Detects SELECT * usage in SQL queries."""
    
    RULE_NAME = "SELECT_STAR"
    RULE_DESCRIPTION = "Avoid SELECT *. Explicitly list columns."
    SEVERITY = "WARNING"
    
    @staticmethod
    def check(sql: str, file_name: str = "") -> List[LintResult]:
        """
        Check for SELECT * instances in SQL.
        
        Args:
            sql: SQL query string to check
            file_name: Optional file name for reporting
            
        Returns:
            List of LintResult objects with violations
        """
        violations = []
        lines = sql.split('\n')
        
        # Pattern to match SELECT * (case-insensitive, accounting for whitespace)
        pattern = r'\bselect\s+\*'
        
        for line_num, line in enumerate(lines, start=1):
            matches = re.finditer(pattern, line, re.IGNORECASE)
            for match in matches:
                result = LintResult(
                    rule=RuleSelectStar.RULE_NAME,
                    severity=RuleSelectStar.SEVERITY,
                    line=line_num,
                    file=file_name,
                    message="Avoid SELECT *. Explicitly list columns.",
                    description=RuleSelectStar.RULE_DESCRIPTION
                )
                violations.append(result)
        
        return violations
    
    @staticmethod
    def format_report(violations: List[LintResult]) -> str:
        """
        Format violations into a readable report.
        
        Args:
            violations: List of LintResult objects
            
        Returns:
            Formatted report string
        """
        if not violations:
            return f"No {RuleSelectStar.RULE_NAME} violations found\n"
        
        report = f"\n{'='*60}\n"
        report += f"Rule: {RuleSelectStar.RULE_NAME}\n"
        report += f"Description: {RuleSelectStar.RULE_DESCRIPTION}\n"
        report += f"Severity: {RuleSelectStar.SEVERITY}\n"
        report += f"{'='*60}\n"
        report += f"Found {len(violations)} violation(s):\n\n"
        
        for violation in violations:
            report += f"  File: {violation.file}\n"
            report += f"  Line {violation.line}: {violation.message}\n"
            report += "\n"
        
        return report

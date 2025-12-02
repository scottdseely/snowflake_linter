"""
Rule: LIMIT without ORDER BY Detection

This rule detects queries that use LIMIT without an ORDER BY clause.
Without ORDER BY, LIMIT results may be nondeterministic across executions.

Example violations:
  SELECT * FROM table LIMIT 10;
  → No ORDER BY before LIMIT

Example valid:
  SELECT * FROM table ORDER BY id LIMIT 10;
  → Has ORDER BY before LIMIT
"""

import re
from typing import List, Dict, Any
try:
    from utils.sql_utils import normalize_sql
except ImportError:
    from ..utils.sql_utils import normalize_sql


class RuleLimitWithoutOrderBy:
    """Detects LIMIT without ORDER BY in SQL queries."""
    
    RULE_NAME = "LIMIT_WITHOUT_ORDER_BY"
    RULE_DESCRIPTION = "LIMIT should be used with ORDER BY to ensure deterministic results"
    SEVERITY = "WARNING"
    
    @staticmethod
    def has_limit(sql: str) -> bool:
        """
        Check if SQL contains LIMIT clause (not as a column alias).
        
        Args:
            sql: SQL query string
            
        Returns:
            True if LIMIT clause is found, False otherwise
        """
        # Look for LIMIT followed by a number or expression (not just used as a name)
        pattern = r'\bLIMIT\s+(\d+|[\w.]+)'
        return bool(re.search(pattern, sql, re.IGNORECASE))
    
    @staticmethod
    def has_order_by(sql: str) -> bool:
        """
        Check if SQL contains ORDER BY clause.
        
        Args:
            sql: SQL query string
            
        Returns:
            True if ORDER BY is found, False otherwise
        """
        pattern = r'\bORDER\s+BY\b'
        return bool(re.search(pattern, sql, re.IGNORECASE))
    
    @staticmethod
    def find_limit_line(sql: str) -> int:
        """
        Find the line number where LIMIT first appears.
        
        Args:
            sql: SQL query string
            
        Returns:
            Line number (1-indexed) where LIMIT is found, or 0 if not found
        """
        lines = sql.split('\n')
        pattern = r'\bLIMIT\b'
        
        for line_num, line in enumerate(lines, start=1):
            if re.search(pattern, line, re.IGNORECASE):
                return line_num
        
        return 0
    
    @staticmethod
    def check(sql: str, file_name: str = "") -> List[Dict[str, Any]]:
        """
        Check for LIMIT without ORDER BY in SQL.
        
        Args:
            sql: SQL query string to check
            file_name: Optional file name for reporting
            
        Returns:
            List of violation dictionaries
        """
        violations = []
        
        # Normalize SQL (remove comments)
        normalized_sql = normalize_sql(sql)
        
        # Check if query has LIMIT
        if not RuleLimitWithoutOrderBy.has_limit(normalized_sql):
            return violations
        
        # Check if query has ORDER BY
        if not RuleLimitWithoutOrderBy.has_order_by(normalized_sql):
            # Find which line the LIMIT is on
            limit_line = RuleLimitWithoutOrderBy.find_limit_line(normalized_sql)
            
            if limit_line > 0:
                violation = {
                    "rule": RuleLimitWithoutOrderBy.RULE_NAME,
                    "severity": RuleLimitWithoutOrderBy.SEVERITY,
                    "line": limit_line,
                    "file": file_name,
                    "message": "LIMIT used without ORDER BY — results may be nondeterministic.",
                    "description": RuleLimitWithoutOrderBy.RULE_DESCRIPTION
                }
                violations.append(violation)
        
        return violations
    
    @staticmethod
    def format_report(violations: List[Dict[str, Any]]) -> str:
        """
        Format violations into a readable report.
        
        Args:
            violations: List of violation dictionaries
            
        Returns:
            Formatted report string
        """
        if not violations:
            return f"✓ No {RuleLimitWithoutOrderBy.RULE_NAME} violations found\n"
        
        report = f"\n{'='*60}\n"
        report += f"Rule: {RuleLimitWithoutOrderBy.RULE_NAME}\n"
        report += f"Description: {RuleLimitWithoutOrderBy.RULE_DESCRIPTION}\n"
        report += f"Severity: {RuleLimitWithoutOrderBy.SEVERITY}\n"
        report += f"{'='*60}\n"
        report += f"Found {len(violations)} violation(s):\n\n"
        
        for violation in violations:
            report += f"  File: {violation.get('file', 'unknown')}\n"
            report += f"  Line {violation['line']}: {violation['message']}\n"
            report += "\n"
        
        return report

"""
Rule: Window Function ORDER BY Detection

This rule detects window functions that lack ORDER BY in their OVER() clause.
Window functions like ROW_NUMBER(), RANK(), DENSE_RANK(), LAG(), LEAD()
typically require ORDER BY to produce meaningful results.

Example violation:
  SELECT ROW_NUMBER() OVER (PARTITION BY customer) AS rn
  → Missing ORDER BY in OVER() clause
"""

import re
from typing import List
try:
    from models.lint_result import LintResult
    from utils.sql_utils import normalize_sql
except ImportError:
    from ..models.lint_result import LintResult
    from ..utils.sql_utils import normalize_sql


class RuleWindowOrderBy:
    """Detects window functions without ORDER BY in OVER() clause."""
    
    RULE_NAME = "WINDOW_MISSING_ORDER_BY"
    RULE_DESCRIPTION = "Window functions should include ORDER BY in OVER() clause"
    SEVERITY = "WARNING"
    
    # Window functions that typically require ORDER BY
    WINDOW_FUNCTIONS = {'ROW_NUMBER', 'RANK', 'DENSE_RANK', 'LAG', 'LEAD', 'NTILE', 
                        'FIRST_VALUE', 'LAST_VALUE', 'NTH_VALUE'}
    
    @staticmethod
    def find_window_functions_with_over(sql: str) -> List[tuple]:
        """
        Find all window function calls with their OVER clauses.
        
        Args:
            sql: SQL query string
            
        Returns:
            List of tuples (line_number, window_func_name, over_clause)
        """
        lines = sql.split('\n')
        results = []
        
        # Pattern to match window functions followed by OVER clause
        # Matches: ROW_NUMBER() OVER (...), LAG(amount) OVER (...), RANK() OVER (...), etc.
        # Pattern explanation: function_name ( any_content ) OVER (
        pattern = r'(\w+)\s*\([^)]*\)\s*OVER\s*\('
        
        for line_num, line in enumerate(lines, start=1):
            # Find all matches on this line
            matches = re.finditer(pattern, line, re.IGNORECASE)
            
            for match in matches:
                # Extract function name from the match
                func_match = re.search(r'(\w+)\s*\(', match.group(0))
                if func_match:
                    func_name = func_match.group(1)
                    
                    # Check if it's a window function we care about
                    if func_name.upper() in RuleWindowOrderBy.WINDOW_FUNCTIONS:
                        # Find the matching closing paren for OVER(...)
                        over_start = match.end() - 1  # Position of opening paren
                        over_clause = RuleWindowOrderBy._extract_over_clause(line, over_start)
                        
                        if over_clause is not None:
                            results.append((line_num, func_name, over_clause))
        
        return results
    
    @staticmethod
    def _extract_over_clause(line: str, paren_start: int) -> str:
        """
        Extract the complete OVER(...) clause from a line.
        
        Args:
            line: The line of SQL text
            paren_start: Index of the opening parenthesis
            
        Returns:
            The content inside OVER(...), or None if unmatched
        """
        if paren_start >= len(line):
            return None
        
        paren_count = 1
        pos = paren_start + 1
        
        # Find matching closing parenthesis
        while pos < len(line) and paren_count > 0:
            if line[pos] == '(':
                paren_count += 1
            elif line[pos] == ')':
                paren_count -= 1
            pos += 1
        
        if paren_count == 0:
            # Return content between parentheses
            return line[paren_start + 1:pos - 1]
        
        # Unmatched parenthesis - return what we have
        return line[paren_start + 1:]
    
    @staticmethod
    def has_order_by(over_clause: str) -> bool:
        """
        Check if OVER clause contains ORDER BY.
        
        Args:
            over_clause: Content of OVER(...) clause
            
        Returns:
            True if ORDER BY is present, False otherwise
        """
        # Simple case-insensitive check for ORDER BY
        pattern = r'\bORDER\s+BY\b'
        return bool(re.search(pattern, over_clause, re.IGNORECASE))
    
    @staticmethod
    def check(sql: str, file_name: str = "") -> List[LintResult]:
        """
        Check for window functions without ORDER BY in OVER clause.
        
        Args:
            sql: SQL query string to check
            file_name: Optional file name for reporting
            
        Returns:
            List of LintResult objects with violations
        """
        violations = []
        
        # Normalize SQL (remove comments)
        normalized_sql = normalize_sql(sql)
        
        # Find all window functions with OVER clauses
        window_funcs = RuleWindowOrderBy.find_window_functions_with_over(normalized_sql)
        
        # Check each window function
        for line_num, func_name, over_clause in window_funcs:
            if not RuleWindowOrderBy.has_order_by(over_clause):
                result = LintResult(
                    rule=RuleWindowOrderBy.RULE_NAME,
                    severity=RuleWindowOrderBy.SEVERITY,
                    line=line_num,
                    file=file_name,
                    message="Window function missing ORDER BY in OVER() clause.",
                    description=RuleWindowOrderBy.RULE_DESCRIPTION
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
            return f"✓ No {RuleWindowOrderBy.RULE_NAME} violations found\n"
        
        report = f"\n{'='*60}\n"
        report += f"Rule: {RuleWindowOrderBy.RULE_NAME}\n"
        report += f"Description: {RuleWindowOrderBy.RULE_DESCRIPTION}\n"
        report += f"Severity: {RuleWindowOrderBy.SEVERITY}\n"
        report += f"{'='*60}\n"
        report += f"Found {len(violations)} violation(s):\n\n"
        
        for violation in violations:
            report += f"  File: {violation.file}\n"
            report += f"  Line {violation.line}: {violation.message}\n"
            report += "\n"
        
        return report

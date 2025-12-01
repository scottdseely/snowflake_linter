"""
Rule: Unqualified Columns Detection

This rule detects columns in SELECT statements that are not qualified with a table alias.
Unqualified columns can cause ambiguity when multiple tables are joined.

Phase 1 (Current): Simple detection of unqualified columns when table aliases are present
Phase 2 (Future): Full AST parsing for complex queries
"""

import re
from typing import List, Set, Tuple
try:
    from models.lint_result import LintResult
    from utils.sql_utils import normalize_sql
except ImportError:
    from ..models.lint_result import LintResult
    from ..utils.sql_utils import normalize_sql


class RuleUnqualifiedColumns:
    """Detects unqualified columns in SELECT statements."""
    
    RULE_NAME = "UNQUALIFIED_COLUMNS"
    RULE_DESCRIPTION = "Detects columns that are not qualified with table alias/name"
    SEVERITY = "WARNING"
    
    @staticmethod
    def extract_table_aliases(sql: str) -> Set[str]:
        """
        Extract table aliases from FROM clause.
        
        Args:
            sql: SQL query string
            
        Returns:
            Set of table aliases found
        """
        aliases = set()
        
        # Pattern to match: FROM table_name alias or table_name AS alias
        # Matches: FROM table1 t, FROM schema.table1 t, FROM table1 AS t
        pattern = r'FROM\s+[\w.]+\s+(?:AS\s+)?(\w+)'
        matches = re.finditer(pattern, sql, re.IGNORECASE)
        
        for match in matches:
            alias = match.group(1)
            # Avoid capturing SQL keywords
            if alias.upper() not in ('WHERE', 'JOIN', 'LEFT', 'RIGHT', 'INNER', 'OUTER', 'ON', 'GROUP', 'ORDER', 'LIMIT'):
                aliases.add(alias)
        
        return aliases
    
    @staticmethod
    def extract_select_columns(sql: str) -> List[Tuple[int, str]]:
        """
        Extract column references from SELECT clause.
        
        Args:
            sql: SQL query string
            
        Returns:
            List of tuples (line_number, column_name)
        """
        lines = sql.split('\n')
        columns = []
        
        in_select = False
        select_start_line = 0
        
        for line_num, line in enumerate(lines, start=1):
            # Check if SELECT starts on this line
            if re.search(r'\bSELECT\b', line, re.IGNORECASE):
                in_select = True
                select_start_line = line_num
            
            # Stop at FROM, WHERE, GROUP BY, ORDER BY, etc.
            if in_select and re.search(r'\b(FROM|WHERE|GROUP\s+BY|ORDER\s+BY|LIMIT|HAVING)\b', line, re.IGNORECASE):
                in_select = False
            
            if in_select:
                # Extract column names: word characters, dots (for qualified columns)
                # Match: col, t.col, schema.table.col, CAST(...), COUNT(*), etc.
                col_pattern = r'(?:^|[,\s(])([\w.]+)(?:\s|,|$|\))'
                matches = re.finditer(col_pattern, line)
                
                for match in matches:
                    col_ref = match.group(1).strip()
                    
                    # Skip empty strings, SQL keywords, and numeric literals
                    if col_ref and not re.match(r'^\d+$', col_ref) and col_ref.upper() not in ('SELECT', 'DISTINCT', 'AS'):
                        columns.append((line_num, col_ref))
        
        return columns
    
    @staticmethod
    def is_unqualified(column: str) -> bool:
        """
        Check if column is unqualified (no table prefix).
        
        Args:
            column: Column reference (e.g., 'col1' or 't.col1')
            
        Returns:
            True if unqualified, False if qualified or special
        """
        # Skip aggregates and functions
        if re.match(r'^(COUNT|SUM|AVG|MAX|MIN|DISTINCT|CAST|CASE|WHEN|THEN|ELSE|END)\b', column, re.IGNORECASE):
            return False
        
        # Skip constants and special values
        if column in ('*', 'NULL', 'TRUE', 'FALSE'):
            return False
        
        # Check if it has a dot (qualified)
        if '.' in column:
            return False
        
        # It's unqualified
        return True
    
    @staticmethod
    def check(sql: str, file_name: str = "") -> List[LintResult]:
        """
        Check for unqualified columns in SQL.
        
        Args:
            sql: SQL query string to check
            file_name: Optional file name for reporting
            
        Returns:
            List of LintResult objects with violations
        """
        violations = []
        
        # Normalize SQL (remove comments)
        normalized_sql = normalize_sql(sql)
        
        # Extract table aliases from FROM clause
        aliases = RuleUnqualifiedColumns.extract_table_aliases(normalized_sql)
        
        # Only check if we found table aliases
        if not aliases:
            return violations
        
        # Extract columns from SELECT clause
        columns = RuleUnqualifiedColumns.extract_select_columns(normalized_sql)
        
        # Check each column
        seen = set()  # Avoid duplicate reports for same column on same line
        for line_num, column in columns:
            if RuleUnqualifiedColumns.is_unqualified(column):
                key = (line_num, column)
                if key not in seen:
                    result = LintResult(
                        rule=RuleUnqualifiedColumns.RULE_NAME,
                        severity=RuleUnqualifiedColumns.SEVERITY,
                        line=line_num,
                        file=file_name,
                        message="Column appears unqualified. Use table alias.",
                        description=RuleUnqualifiedColumns.RULE_DESCRIPTION
                    )
                    violations.append(result)
                    seen.add(key)
        
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
            return f"✓ No {RuleUnqualifiedColumns.RULE_NAME} violations found\n"
        
        report = f"\n{'='*60}\n"
        report += f"Rule: {RuleUnqualifiedColumns.RULE_NAME}\n"
        report += f"Description: {RuleUnqualifiedColumns.RULE_DESCRIPTION}\n"
        report += f"Severity: {RuleUnqualifiedColumns.SEVERITY}\n"
        report += f"{'='*60}\n"
        report += f"Found {len(violations)} violation(s):\n\n"
        
        for violation in violations:
            report += f"  File: {violation.file}\n"
            report += f"  Line {violation.line}: {violation.message}\n"
            report += "\n"
        
        return report

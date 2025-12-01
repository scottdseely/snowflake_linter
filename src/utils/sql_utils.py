import re
from typing import List, Tuple

def find_select_star_instances(sql: str) -> List[Tuple[int, str]]:
    """
    Find all instances of SELECT * in SQL code.
    
    Args:
        sql: SQL query string
        
    Returns:
        List of tuples containing (line_number, matched_text)
    """
    lines = sql.split('\n')
    instances = []
    
    # Pattern to match SELECT * (case-insensitive, accounting for whitespace)
    # No word boundary after * since * is not a word character
    pattern = r'\bselect\s+\*'
    
    for line_num, line in enumerate(lines, start=1):
        matches = re.finditer(pattern, line, re.IGNORECASE)
        for match in matches:
            instances.append((line_num, match.group()))
    
    return instances


def normalize_sql(sql: str) -> str:
    """
    Normalize SQL for parsing (remove comments, extra whitespace).
    
    Args:
        sql: Raw SQL string
        
    Returns:
        Normalized SQL string
    """
    # Remove SQL comments
    sql = re.sub(r'--.*?$', '', sql, flags=re.MULTILINE)  # Remove -- comments
    sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)  # Remove /* */ comments
    return sql

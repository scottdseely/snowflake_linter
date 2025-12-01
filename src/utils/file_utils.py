import os
from typing import List


def read_sql_file(file_path: str) -> str:
    """
    Read SQL file content.
    
    Args:
        file_path: Path to SQL file
        
    Returns:
        File content as string
        
    Raises:
        FileNotFoundError: If file does not exist
        IOError: If unable to read file
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def get_sql_files(directory: str) -> List[str]:
    """
    Get all SQL files in a directory.
    
    Args:
        directory: Directory path to search
        
    Returns:
        List of SQL file paths
    """
    sql_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.sql'):
                sql_files.append(os.path.join(root, file))
    return sql_files


def write_report(report_path: str, content: str) -> None:
    """
    Write report to file.
    
    Args:
        report_path: Path where report will be written
        content: Report content
    """
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(content)

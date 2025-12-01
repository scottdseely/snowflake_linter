#!/usr/bin/env python3
"""
Quick test script to demonstrate the CLI works
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from linter import SnowflakeLinter

if __name__ == '__main__':
    linter = SnowflakeLinter()
    
    print(f"\n{'='*60}")
    print(f"Snowflake SQL Linter - Test")
    print(f"{'='*60}")
    print(f"Loaded {len(linter.rules)} rule(s):")
    for rule in linter.rules:
        if hasattr(rule, 'RULE_NAME'):
            print(f"  - {rule.RULE_NAME}")
    
    print("\nLinting samples directory...")
    violations = linter.lint_directory('./samples')
    
    print(f"\nFound {len(violations)} total violations:")
    for v in violations:
        print(f"  {v['file']} (Line {v['line']}): {v['message']}")
    
    linter.print_summary()

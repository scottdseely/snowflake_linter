"""
Main Snowflake SQL Linter

Orchestrates linting rules and generates reports.
"""

import os
import sys
import importlib
import inspect
from typing import List, Dict, Any
from pathlib import Path
from utils.file_utils import read_sql_file, get_sql_files, write_report


class SnowflakeLinter:
    """Main linter class that applies rules to SQL files."""
    
    def __init__(self):
        self.rules = self._load_rules_dynamically()
        self.violations = []
    
    @staticmethod
    def _load_rules_dynamically() -> List[Any]:
        """
        Dynamically load all rule classes from the rules folder.
        
        Returns:
            List of instantiated rule objects
        """
        rules = []
        rules_dir = Path(__file__).parent / 'rules'
        
        # Add src directory to sys.path to allow relative imports
        src_dir = Path(__file__).parent
        if str(src_dir) not in sys.path:
            sys.path.insert(0, str(src_dir))
        
        try:
            if not rules_dir.exists():
                return rules
            
            for file_name in os.listdir(rules_dir):
                # Skip __init__.py and non-python files
                if file_name.startswith('rule_') and file_name.endswith('.py'):
                    module_name = file_name[:-3]  # Remove .py extension
                    
                    try:
                        # Import the module dynamically
                        module = importlib.import_module(f'rules.{module_name}')
                        
                        # Find all classes in the module that start with 'Rule'
                        for name, obj in inspect.getmembers(module, inspect.isclass):
                            # Check if it's a Rule class and has check method and RULE_NAME
                            if name.startswith('Rule') and hasattr(obj, 'check') and hasattr(obj, 'RULE_NAME'):
                                # Instantiate the rule and add to list
                                rule_instance = obj()
                                rules.append(rule_instance)
                    except Exception as e:
                        print(f"Warning: Failed to load rule module '{module_name}': {str(e)}", file=sys.stderr)
        finally:
            pass
        
        return rules
    
    def lint_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Lint a single SQL file.
        
        Args:
            file_path: Path to SQL file
            
        Returns:
            List of violations found
        """
        try:
            sql_content = read_sql_file(file_path)
            file_violations = []
            
            for rule in self.rules:
                violations = rule.check(sql_content, file_path)
                file_violations.extend(violations)
            
            return file_violations
        except Exception as e:
            print(f"Error linting file {file_path}: {str(e)}")
            return []
    
    def lint_directory(self, directory: str) -> List[Dict[str, Any]]:
        """
        Lint all SQL files in a directory.
        
        Args:
            directory: Directory path to lint
            
        Returns:
            List of all violations found
        """
        sql_files = get_sql_files(directory)
        all_violations = []
        
        for sql_file in sql_files:
            violations = self.lint_file(sql_file)
            all_violations.extend(violations)
        
        self.violations = all_violations
        return all_violations
    
    def generate_report(self, output_path: str) -> None:
        """
        Generate and write linting report.
        
        Args:
            output_path: Path where report will be written
        """
        report = "SNOWFLAKE SQL LINTER REPORT\n"
        report += "=" * 60 + "\n\n"
        
        if not self.violations:
            report += "✓ No violations found!\n"
        else:
            # Group violations by rule
            violations_by_rule = {}
            for violation in self.violations:
                rule_name = violation['rule']
                if rule_name not in violations_by_rule:
                    violations_by_rule[rule_name] = []
                violations_by_rule[rule_name].append(violation)
            
            # Generate report for each rule using its formatter
            for rule_name in sorted(violations_by_rule.keys()):
                violations = violations_by_rule[rule_name]
                
                # Find the rule object and use its format_report method
                for rule in self.rules:
                    if hasattr(rule, 'RULE_NAME') and rule.RULE_NAME == rule_name:
                        if hasattr(rule, 'format_report'):
                            report += rule.format_report(violations)
                        else:
                            # Fallback formatting if rule doesn't have format_report
                            report += f"\n{'='*60}\n"
                            report += f"Rule: {rule_name}\n"
                            report += f"{'='*60}\n"
                            report += f"Found {len(violations)} violation(s):\n\n"
                            for v in violations:
                                report += f"  {v.get('file', 'unknown')} (Line {v['line']}): {v['message']}\n"
                        break
        
        write_report(output_path, report)
        print(f"Report written to: {output_path}")
    
    def print_violations(self) -> None:
        """Print violations to console."""
        if not self.violations:
            print("✓ No violations found!")
            return
        
        print(f"\nFound {len(self.violations)} violation(s):\n")
        for violation in self.violations:
            print(f"  {violation['file']} (Line {violation['line']}): {violation['message']}")
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of linting results.
        
        Returns:
            Dictionary with summary statistics
        """
        summary = {
            'total_violations': len(self.violations),
            'violations_by_rule': {},
            'violations_by_severity': {},
            'files_checked': len(set(v.get('file', 'unknown') for v in self.violations))
        }
        
        for violation in self.violations:
            # Count by rule
            rule_name = violation['rule']
            summary['violations_by_rule'][rule_name] = summary['violations_by_rule'].get(rule_name, 0) + 1
            
            # Count by severity
            severity = violation.get('severity', 'UNKNOWN')
            summary['violations_by_severity'][severity] = summary['violations_by_severity'].get(severity, 0) + 1
        
        return summary
    
    def print_summary(self) -> None:
        """Print summary of findings to console."""
        summary = self.get_summary()
        
        print("\n" + "="*60)
        print("LINTING SUMMARY")
        print("="*60)
        print(f"Total violations: {summary['total_violations']}")
        
        if summary['violations_by_rule']:
            print("\nViolations by rule:")
            for rule, count in sorted(summary['violations_by_rule'].items()):
                print(f"  {rule}: {count}")
        
        if summary['violations_by_severity']:
            print("\nViolations by severity:")
            for severity, count in sorted(summary['violations_by_severity'].items()):
                print(f"  {severity}: {count}")
        
        print(f"\nFiles checked: {summary['files_checked']}")
        print("="*60 + "\n")


def main():
    """CLI entry point for the linter."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Snowflake SQL Linter - Analyze SQL for best practices',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python linter.py samples/sample1.sql
  python linter.py samples/
  python linter.py samples/ --report reports/results.txt
        """
    )
    
    parser.add_argument(
        'path',
        help='Path to SQL file or directory containing SQL files'
    )
    
    parser.add_argument(
        '--report',
        '-r',
        help='Output report file path (optional)',
        default=None
    )
    
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Print detailed violation information'
    )
    
    args = parser.parse_args()
    
    # Initialize linter
    linter = SnowflakeLinter()
    
    # Print loaded rules
    print(f"\n{'='*60}")
    print(f"Snowflake SQL Linter")
    print(f"{'='*60}")
    print(f"Loaded {len(linter.rules)} rule(s):")
    for rule in linter.rules:
        if hasattr(rule, 'RULE_NAME'):
            print(f"  ✓ {rule.RULE_NAME}")
    print()
    
    # Resolve path
    path = Path(args.path)
    
    if not path.exists():
        print(f"❌ Error: Path not found: {args.path}")
        sys.exit(1)
    
    # Lint file or directory
    if path.is_file():
        if not path.suffix.lower() == '.sql':
            print(f"Warning: File does not have .sql extension: {path}")
        
        print(f"Linting file: {path}")
        violations = linter.lint_file(str(path))
        linter.violations = violations  # Store in linter object
    elif path.is_dir():
        print(f"Linting directory: {path}")
        violations = linter.lint_directory(str(path))
    else:
        print(f"Error: Path is neither file nor directory: {args.path}")
        sys.exit(1)
    
    # Print results
    print()
    if violations:
        if args.verbose:
            linter.print_violations()
        linter.print_summary()
    else:
        print("No violations found!")
    
    # Generate report if requested
    if args.report:
        linter.generate_report(args.report)
    
    # Exit with appropriate code
    sys.exit(0 if not violations else 1)


if __name__ == "__main__":
    main()

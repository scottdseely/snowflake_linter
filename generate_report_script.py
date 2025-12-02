import sys
sys.path.insert(0, 'src')
from linter import SnowflakeLinter
from utils.file_utils import write_report

l = SnowflakeLinter()
violations = l.lint_directory('samples')
report = 'SNOWFLAKE SQL LINTER REPORT\n'
report += '='*60 + '\n\n'
if not violations:
    report += '✓ No violations found!\n'
else:
    report += f'Total violations: {len(violations)}\n\n'
    # Group by rule
    by_rule = {}
    for v in violations:
        by_rule.setdefault(v['rule'], []).append(v)
    for rule in sorted(by_rule.keys()):
        report += '='*40 + '\n'
        report += f'Rule: {rule} (Found {len(by_rule[rule])})\n'
        report += '-'*40 + '\n'
        for vv in by_rule[rule]:
            report += f"File: {vv.get('file','unknown')}  Line {vv.get('line')}  Severity: {vv.get('severity','') }\n"
            report += f"  {vv.get('message')}\n\n"

out_path = 'reports/results.txt'
write_report(out_path, report)
print('Wrote report to', out_path)
# Print first 40 lines
for i, line in enumerate(report.splitlines()):
    if i<40:
        print(line)

import re

test_sql = """SELECT amount, o.total
FROM orders o"""

lines = test_sql.split('\n')

for line_num, line in enumerate(lines, start=1):
    print(f"Line {line_num}: {repr(line)}")
    
    # Better pattern - match word characters followed by:
    # - a space/comma/paren or end of string
    col_pattern = r'(?:^|[,\s(])([\w.]+?)(?=[,\s)$]|$)'
    matches = re.finditer(col_pattern, line)
    
    print(f"  Improved regex matches:")
    for match in matches:
        col_ref = match.group(1).strip()
        if col_ref:
            print(f"    - '{col_ref}'")
    print()

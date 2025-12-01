# Snowflake SQL Linter

A lightweight SQL linter focused on Snowflake best practices and SQL quality improvements.

## Features

This initial version analyzes `.sql` files and reports issues such as:

- **SELECT \*** - Detects `SELECT *` statements which should be avoided
- **Unqualified columns** - Flags columns not qualified with table alias/name when multiple tables are present
- **Window functions missing ORDER BY** - Ensures window functions have ORDER BY clause
- **LIMIT without ORDER BY** - Detects LIMIT without ORDER BY (results may be unpredictable)
- **Non-capitalized SQL keywords** - Ensures SQL keywords are properly capitalized

## Installation

No external dependencies required. Python 3.7+

## Usage

### Command Line

Lint a single SQL file:
```bash
python src/linter.py samples/sample1.sql
```

Lint all SQL files in a directory:
```bash
python src/linter.py samples/
```

Show detailed violations:
```bash
python src/linter.py samples/ --verbose
```

Generate a report file:
```bash
python src/linter.py samples/ --report reports/linting_report.txt
```

Run as a module:
```bash
python -m src samples/
```

### Programmatic Usage

```python
from src.linter import SnowflakeLinter

linter = SnowflakeLinter()

# Lint a file
violations = linter.lint_file('query.sql')

# Lint a directory
violations = linter.lint_directory('./sql_files')

# Print summary
linter.print_summary()

# Generate report
linter.generate_report('report.txt')
```

## Project Structure

```
snowflake_linter/
├── README.md
├── src/
│   ├── __main__.py              # Module entry point
│   ├── linter.py                # Main linter orchestrator
│   ├── rules/                   # Linting rules
│   │   ├── __init__.py
│   │   ├── rule_select_star.py
│   │   ├── rule_unqualified_columns.py
│   │   ├── rule_window_orderby.py
│   │   ├── rule_limit_without_orderby.py
│   │   └── rule_keyword_case.py
│   ├── utils/                   # Utility functions
│   │   ├── sql_utils.py         # SQL parsing utilities
│   │   └── file_utils.py        # File handling utilities
│   └── models/                  # Data models
│       ├── lint_result.py       # Single linting result
│       └── lint_report.py       # Complete linting report
├── samples/
│   ├── sample1.sql
│   └── sample2.sql
└── reports/                     # Auto-generated reports
```

## Rules

### SELECT_STAR
Detects `SELECT *` which should be avoided as it:
- Makes code fragile to schema changes
- Includes unnecessary columns
- Can impact performance

**Example:**
```sql
SELECT *              -- VIOLATION
FROM customers c;
```

### UNQUALIFIED_COLUMNS
Flags columns not qualified with table alias when multiple tables are present.

**Example:**
```sql
SELECT col1, t.col2   -- col1 flagged (unqualified)
FROM table1 t
JOIN table2 t2 ON t.id = t2.id;
```

## Current Implementation Notes

- **Phase 1**: Simple regex-based pattern matching
- **Phase 2** (Future): Full AST parsing for complex queries
- Rules are dynamically loaded from the `rules/` folder
- Violations are combined from all active rules

## Exit Codes

- `0` - Linting completed successfully with no violations
- `1` - Linting completed with violations found

## Contributing

To add a new rule:

1. Create a new file in `src/rules/` named `rule_<name>.py`
2. Implement a class `Rule<Name>` with:
   - `RULE_NAME` constant
   - `RULE_DESCRIPTION` constant
   - `SEVERITY` constant
   - `check(sql, file_name)` static method
   - `format_report(violations)` static method

The linter will automatically discover and load it.

## License

MIT

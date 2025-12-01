from src.rules.rule_unqualified_columns import RuleUnqualifiedColumns

# Test 1: Basic case from requirements
test_sql1 = """SELECT amount, o.total
FROM orders o"""

# Test 2: Multiple unqualified columns
test_sql2 = """SELECT name, amount, c.id
FROM customers c, orders o
WHERE c.id = o.customer_id"""

# Test 3: No aliases (should return no violations)
test_sql3 = """SELECT amount, total
FROM orders"""

# Test 4: All qualified columns
test_sql4 = """SELECT o.amount, o.total
FROM orders o"""

tests = [
    ("Basic case", test_sql1),
    ("Multiple unqualified", test_sql2),
    ("No aliases", test_sql3),
    ("All qualified", test_sql4),
]

for test_name, sql in tests:
    print(f"\n{'='*50}")
    print(f"Test: {test_name}")
    print(f"{'='*50}")
    print(f"SQL:\n{sql}")
    
    results = RuleUnqualifiedColumns.check(sql, 'test.sql')
    print(f"\nViolations: {len(results)}")
    for r in results:
        print(f"  Line {r.line}: {r.message}")


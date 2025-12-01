-- Sample SQL with multiple violations
SELECT col1, col2, t.col3
FROM table1 t
LEFT JOIN table2 t2 ON t.id = t2.id
WHERE col1 > 100
AND col2 = 'test'
SELECT * FROM another_table;

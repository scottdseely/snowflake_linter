-- Sample SQL query with violations
SELECT *
FROM customers c
JOIN orders o ON c.id = o.customer_id
WHERE order_date > '2024-01-01'
ORDER BY order_id;

-- Good SQL query with proper practices
SELECT 
    c.customer_id,
    c.name,
    o.order_id,
    o.order_date
FROM customers c
JOIN orders o ON c.id = o.customer_id
WHERE o.order_date > '2024-01-01'
ORDER BY c.customer_id, o.order_date;

EXPLAIN ANALYZE
SELECT * FROM payments
ORDER BY amount DESC
LIMIT 10


EXPLAIN ANALYZE
SELECT s.server_id, o.order_id, p.payment_id FROM servers s
JOIN orders o ON o.server_id=s.server_id
JOIN payments p ON p.order_id=o.order_id
WHERE s.server_id=2 AND (s.status='available' AND (o.status='pending' OR p.status='pending')

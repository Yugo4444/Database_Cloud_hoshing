CREATE OR REPLACE VIEW v_customer_overview AS
SELECT 
    u.user_id,
    u.first_name || ' ' || u.last_name AS full_name,
    u.email,
    COUNT(DISTINCT o.order_id) AS total_orders,
    COALESCE(SUM(p.amount) FILTER (WHERE p.status = 'completed'), 0) AS total_paid,
    COUNT(DISTINCT t.ticket_id) FILTER (WHERE t.status != 'closed') AS active_tickets
FROM Users u
LEFT JOIN Orders o ON u.user_id = o.user_id
LEFT JOIN Payments p ON o.order_id = p.order_id
LEFT JOIN SupportTickets t ON u.user_id = t.user_id
GROUP BY u.user_id;


CREATE OR REPLACE VIEW v_active_rentals AS
SELECT 
    o.order_id,
    u.email AS customer_email,
    s.name AS server_name,
    s.ip_address,
    st.type_name,
    o.start_time,
    o.end_time,
    st.price_per_hour
FROM Orders o
JOIN Users u ON o.user_id = u.user_id
JOIN Servers s ON o.server_id = s.server_id
JOIN ServerTypes st ON s.server_type_id = st.server_type_id
WHERE o.status = 'active' AND s.status = 'rented';


CREATE OR REPLACE VIEW v_fleet_capacity AS
SELECT 
    st.type_name,
    COUNT(s.server_id) AS total_servers,
    COUNT(s.server_id) FILTER (WHERE s.status = 'available') AS available_now,
    COUNT(s.server_id) FILTER (WHERE s.status = 'rented') AS currently_rented,
    COUNT(s.server_id) FILTER (WHERE s.status = 'maintenance') AS under_maintenance,
    CASE 
        WHEN COUNT(s.server_id) > 0 
        THEN ROUND((COUNT(s.server_id) FILTER (WHERE s.status = 'rented')::NUMERIC / COUNT(s.server_id) * 100), 2)
        ELSE 0 
    END AS occupancy_rate_percent
FROM ServerTypes st
LEFT JOIN Servers s ON st.server_type_id = s.server_type_id
GROUP BY st.server_type_id, st.type_name;


CREATE OR REPLACE VIEW v_server_profitability AS
SELECT 
    s.server_id,
    s.name AS server_name,
    st.type_name,
    COALESCE(SUM(p.amount), 0) AS total_earned,
    COUNT(DISTINCT o.order_id) FILTER (WHERE p.status = 'completed') AS successful_rentals_count
FROM Servers s
JOIN ServerTypes st ON s.server_type_id = st.server_type_id
LEFT JOIN Orders o ON s.server_id = o.server_id
LEFT JOIN Payments p ON o.order_id = p.order_id
GROUP BY s.server_id, s.name, st.type_name
ORDER BY total_earned DESC;
CREATE OR REPLACE FUNCTION fn_get_order_total(p_order_id INTEGER)
RETURNS NUMERIC(12, 2) AS $$
DECLARE
    v_total NUMERIC;
BEGIN
    SELECT 
        (EXTRACT(EPOCH FROM (o.end_time - o.start_time)) / 3600) * st.price_per_hour
    INTO v_total
    FROM Orders o
    JOIN Servers s ON o.server_id = s.server_id
    JOIN ServerTypes st ON s.server_type_id = st.server_type_id
    WHERE o.order_id = p_order_id;

    RETURN ROUND(COALESCE(v_total, 0), 2);
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION fn_find_free_servers(
    p_server_type_id INTEGER, 
    p_start TIMESTAMP WITH TIME ZONE, 
    p_end TIMESTAMP WITH TIME ZONE
)
RETURNS TABLE (
    free_server_id INTEGER,
    server_name    VARCHAR(200),
    ip             INET,
    type_name      VARCHAR(100)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        s.server_id, 
        s.name, 
        s.ip_address,
        st.type_name
    FROM Servers s
    JOIN ServerTypes st ON s.server_type_id = st.server_type_id
    WHERE s.server_type_id = p_server_type_id
      AND s.status != 'maintenance'
      AND s.server_id NOT IN (
          SELECT o.server_id
          FROM Orders o
          WHERE o.status IN ('active', 'pending')
            AND (o.start_time <= p_end AND o.end_time >= p_start)
      );
END;
$$ LANGUAGE plpgsql;
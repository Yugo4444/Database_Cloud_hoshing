-- ---------- SERVER TYPES ----------
INSERT INTO ServerTypes (type_name, description, price_per_hour, discount, support_level) VALUES
('nano',     '1 vCPU, 512MB RAM - dev/test', 0.02, 0.00, 'basic'),
('micro',    '1 vCPU, 1GB RAM', 0.05, 1, 'basic'),
('small',    '2 vCPU, 2GB RAM', 0.12, 1, 'standard'),
('medium',   '4 vCPU, 8GB RAM', 0.35, 1, 'standard'),
('large',    '8 vCPU, 16GB RAM', 0.70, 1, 'premium'),
('xlarge',   '16 vCPU, 32GB RAM', 1.40, 1, 'premium'),
('dedicated','Bare metal, 32+ vCPU', 4.00, 1, 'premium');


-- ---------- USERS ----------
INSERT INTO Users (first_name, last_name, email, phone, role)
SELECT
    'FirstName' || i,
    'LastName' || i,
    'user' || i || '@example.com',
    CASE WHEN random() < 0.7 THEN '+1-' || (5000000000 + (random() * 999999999)::bigint)::text ELSE NULL END,
    (ARRAY['customer','customer','customer','admin','operator','support'])[1 + (random() * 5)::int]
FROM generate_series(1, 1000) AS i;


-- ---------- SERVERS ----------
INSERT INTO Servers (name, server_type_id, ip_address, status)
SELECT
    'srv-' || i || '-' || substr(md5(random()::text), 1, 6),
    1 + (random() * 6)::int,
    (
        '10.' || (1 + floor(random() * 254))::int || '.' ||
        (1 + floor(random() * 254))::int || '.' ||
        (1 + floor(random() * 254))::int
    )::inet,
    (ARRAY['available','available','available','available','maintenance','offline'])[1 + (random() * 5)::int]
FROM generate_series(1, 500) AS i;


-- ---------- ORDERS ----------
INSERT INTO Orders (user_id, server_id, start_time, end_time, status)
SELECT
    base.user_id,
    base.server_id,
    base.start_time,
    base.end_time,

    CASE
        WHEN base.end_time < NOW() THEN
            (ARRAY['completed','completed','completed','cancelled'])[1 + floor(random() * 4)::int]
        WHEN base.start_time <= NOW() AND base.end_time > NOW() THEN
            (ARRAY['active','active','cancelled'])[1 + floor(random() * 3)::int]
        ELSE
            (ARRAY['pending','pending','cancelled'])[1 + floor(random() * 3)::int]
    END AS status

FROM (
    SELECT
        1 + floor(random() * 999)::int AS user_id,
        1 + floor(random() * 499)::int AS server_id,
        CURRENT_TIMESTAMP
            + ((floor(random() * 240)::int - 180) || ' days')::interval
            AS start_time,
        (1 + floor(random() * 72)::int) AS duration_hours
    FROM generate_series(1, 5000)
) AS raw

CROSS JOIN LATERAL (
    SELECT
        raw.user_id,
        raw.server_id,
        raw.start_time,
        raw.start_time + raw.duration_hours * interval '1 hour' AS end_time
) AS base
JOIN Servers s ON s.server_id = base.server_id;

-- ---------- PAYMENTS ----------
INSERT INTO Payments (order_id, amount, payment_date, method, status)
SELECT
    o.order_id,
    ROUND(
        EXTRACT(EPOCH FROM (o.end_time - o.start_time)) / 3600
        * st.price_per_hour,
        2
    ) AS amount,
    o.start_time AS payment_date,
    (ARRAY['card','bank_transfer','paypal','crypto'])
        [1 + floor(random() * 4)::int] AS method,
    CASE
        WHEN o.status IN ('completed', 'active') THEN 'completed'
        WHEN o.status = 'cancelled' THEN
            (ARRAY['failed','refunded'])
                [1 + floor(random() * 2)::int]
        WHEN o.status = 'pending' THEN 'pending'
    END AS status
FROM Orders o
JOIN Servers s ON o.server_id = s.server_id
JOIN ServerTypes st ON s.server_type_id = st.server_type_id;


-- ---------- RESOURCES USAGE ----------
INSERT INTO ResourcesUsage (server_id, cpu_used, ram_used, storage_used, timestamp)
SELECT
    s.server_id,
    (random() * 95 + 5)::numeric(5,2),
    (random() * 90 + 10)::numeric(5,2),
    (random() * 80 + 5)::numeric(5,2),
    CURRENT_TIMESTAMP - ((random() * 30)::int || ' days')::interval - ((random() * 86400)::int || ' seconds')::interval
FROM Servers s
CROSS JOIN generate_series(1,12) AS _ 
WHERE random() < 0.8;


-- ---------- SERVER MAINTENANCE ----------
INSERT INTO ServerMaintenance (server_id, performed_by, maintenance_date, description, status)
SELECT
    1 + (random() * 499)::int,
    1 + (random() * 999)::int,
    CURRENT_TIMESTAMP - ((random() * 60)::int || ' days')::interval,
    (ARRAY['Kernel update','Hardware check','Security patch','Backup verification','Network upgrade'])[1 + (random() * 4)::int],
    (ARRAY['scheduled','in_progress','completed','completed','completed'])[1 + (random() * 4)::int]
FROM generate_series(1,500) AS i;


-- ---------- TAGS ----------
INSERT INTO Tags (tag_name) VALUES
('web'),('db'),('cache'),('gpu'),('high-io'),('eu'),('us'),('asia'),('prod'),('staging'),('dev')
ON CONFLICT (tag_name) DO NOTHING;


-- ---------- SERVER TAG ASSIGNMENTS ----------
INSERT INTO ServerTagAssignments (server_id, tag_id)
SELECT
    s.server_id,
    t.tag_id
FROM Servers s
JOIN Tags t ON random() < 0.3
ON CONFLICT (server_id, tag_id) DO NOTHING;


-- ---------- SERVER LOGS ----------
INSERT INTO ServerLogs (server_id, event_type, description, severity, logged_at, performed_by, extra_data)
SELECT
    1 + (random() * 499)::int,
    (ARRAY['reboot','error','update','shutdown','startup'])[1 + floor(random() * 4)::int],
    'Event description ' || i,
    (ARRAY['info','warning','critical'])[1 + floor(random() * 2)::int],
    CURRENT_TIMESTAMP - ((random() * 30)::int || ' days')::interval,
    1 + floor(random() * 999)::int,
    '{"details":"sample"}'::jsonb
FROM generate_series(1,5000) AS i;


-- ---------- SUPPORT TICKETS ----------
INSERT INTO SupportTickets (user_id, subject, description, status, priority, created_at, updated_at)
SELECT
    1 + floor(random() * 999)::int,
    'Issue ' || i,
    'Description of issue ' || i,
    (ARRAY['open','in_progress','resolved','closed'])[1 + floor(random() * 3)::int],
    (ARRAY['low','medium','high','critical'])[1 + floor(random() * 3)::int],
    CURRENT_TIMESTAMP - ((random() * 60)::int || ' days')::interval,
    CURRENT_TIMESTAMP - ((random() * 30)::int || ' days')::interval
FROM generate_series(1,1000) AS i;



UPDATE Servers s
SET status = 'rented'
WHERE EXISTS (
    SELECT 1
    FROM Orders o
    WHERE o.server_id = s.server_id
      AND o.status = 'active'
);


UPDATE Servers s
SET status = 'available'
WHERE s.status != 'rented'
  AND EXISTS (
      SELECT 1
      FROM Orders o
      WHERE o.server_id = s.server_id
        AND o.status = 'pending'
  );
-- ---------- USERS ----------
CREATE INDEX idx_users_role ON Users(role);
CREATE INDEX idx_users_created_at ON Users(created_at);

-- ---------- SERVERS ----------
CREATE INDEX idx_servers_server_type_id ON Servers(server_type_id);
CREATE INDEX idx_servers_status ON Servers(status);
CREATE INDEX idx_servers_created_at ON Servers(created_at);

---------- ORDERS ----------
CREATE INDEX idx_orders_user_id ON Orders(user_id);
CREATE INDEX idx_orders_server_id ON Orders(server_id);
CREATE INDEX idx_orders_status ON Orders(status);
CREATE INDEX idx_orders_start_end_time ON Orders(start_time, end_time);

---------- PAYMENTS ----------
CREATE INDEX idx_payments_order_id ON Payments(order_id);
CREATE INDEX idx_payments_status ON Payments(status);
CREATE INDEX idx_payments_payment_date ON Payments(payment_date);
CREATE INDEX IF NOT EXISTS idx_payments_amount ON payments (amount);

-- ---------- RESOURCES USAGE ----------
CREATE INDEX idx_resourcesusage_server_id ON ResourcesUsage(server_id);
CREATE INDEX idx_resourcesusage_timestamp ON ResourcesUsage(timestamp);

-- ---------- SERVER MAINTENANCE ----------
CREATE INDEX idx_servermaintenance_server_id ON ServerMaintenance(server_id);
CREATE INDEX idx_servermaintenance_performed_by ON ServerMaintenance(performed_by);
CREATE INDEX idx_servermaintenance_date ON ServerMaintenance(maintenance_date);
CREATE INDEX idx_servermaintenance_status ON ServerMaintenance(status);

-- ---------- SERVER TAG ASSIGNMENTS ----------
CREATE INDEX idx_servertagassignments_tag_id ON ServerTagAssignments(tag_id);

-- ---------- AUDIT LOG ----------
CREATE INDEX idx_auditlog_table_name ON AuditLog(table_name);
CREATE INDEX idx_auditlog_record_id ON AuditLog(record_id);
CREATE INDEX idx_auditlog_user_id ON AuditLog(user_id);
CREATE INDEX idx_auditlog_timestamp ON AuditLog(timestamp);

-- ---------- SERVER LOGS ----------
CREATE INDEX idx_serverlogs_server_id ON ServerLogs(server_id);
CREATE INDEX idx_serverlogs_event_type ON ServerLogs(event_type);
CREATE INDEX idx_serverlogs_severity ON ServerLogs(severity);
CREATE INDEX idx_serverlogs_logged_at ON ServerLogs(logged_at);
CREATE INDEX idx_serverlogs_performed_by ON ServerLogs(performed_by);

-- ---------- SUPPORT TICKETS ----------
CREATE INDEX idx_supporttickets_user_id ON SupportTickets(user_id);
CREATE INDEX idx_supporttickets_status ON SupportTickets(status);
CREATE INDEX idx_supporttickets_priority ON SupportTickets(priority);
CREATE INDEX idx_supporttickets_created_at ON SupportTickets(created_at);
CREATE INDEX idx_supporttickets_updated_at ON SupportTickets(updated_at);
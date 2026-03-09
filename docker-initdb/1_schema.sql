-- ---------- SERVER TYPES ----------
CREATE TABLE ServerTypes (
    server_type_id   SERIAL PRIMARY KEY,
    type_name        VARCHAR(100) NOT NULL UNIQUE,
    description      TEXT,
    price_per_hour   NUMERIC(10, 2) NOT NULL CHECK (price_per_hour >= 0),
    discount         NUMERIC(3,2) DEFAULT 0 CHECK (discount >= 0 AND discount <= 1),
    support_level    VARCHAR(20) NOT NULL DEFAULT 'basic' CHECK (support_level IN ('basic', 'standard', 'premium'))
);

-- ---------- USERS ----------
CREATE TABLE Users (
    user_id     SERIAL PRIMARY KEY,
    first_name  VARCHAR(100) NOT NULL,
    last_name   VARCHAR(100) NOT NULL,
    email       VARCHAR(255) NOT NULL UNIQUE,
    phone       VARCHAR(30),
    role        VARCHAR(50) NOT NULL CHECK (role IN ('customer', 'admin', 'operator', 'support')),
    created_at  TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ---------- SERVERS ----------
CREATE TABLE Servers (
    server_id       SERIAL PRIMARY KEY,
    name            VARCHAR(200) NOT NULL,
    server_type_id  INTEGER NOT NULL REFERENCES ServerTypes(server_type_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    ip_address      INET UNIQUE,
    status          VARCHAR(50) NOT NULL CHECK (status IN ('available', 'rented', 'maintenance', 'offline')),
    created_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ---------- ORDERS ----------
CREATE TABLE Orders (
    order_id    SERIAL PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES Users(user_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    server_id   INTEGER NOT NULL REFERENCES Servers(server_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    start_time  TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time    TIMESTAMP WITH TIME ZONE NOT NULL,
    status      VARCHAR(50) NOT NULL CHECK (status IN ('pending', 'active', 'completed', 'cancelled')),
    CONSTRAINT orders_time_range CHECK (end_time > start_time)
);

-- ---------- PAYMENTS ----------
CREATE TABLE Payments (
    payment_id   SERIAL PRIMARY KEY,
    order_id     INTEGER NOT NULL REFERENCES Orders(order_id) ON UPDATE CASCADE ON DELETE CASCADE,
    amount       NUMERIC(12, 2) NOT NULL CHECK (amount > 0),
    payment_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    method       VARCHAR(50) NOT NULL CHECK (method IN ('card', 'bank_transfer', 'paypal', 'crypto')),
    status       VARCHAR(50) NOT NULL CHECK (status IN ('pending', 'completed', 'failed', 'refunded'))
);

-- ---------- RESOURCES USAGE ----------
CREATE TABLE ResourcesUsage (
    usage_id     SERIAL PRIMARY KEY,
    server_id    INTEGER NOT NULL REFERENCES Servers(server_id) ON UPDATE CASCADE ON DELETE CASCADE,
    cpu_used     NUMERIC(5, 2) NOT NULL CHECK (cpu_used >= 0 AND cpu_used <= 100),
    ram_used     NUMERIC(5, 2) NOT NULL CHECK (ram_used >= 0 AND ram_used <= 100),
    storage_used NUMERIC(5, 2) NOT NULL CHECK (storage_used >= 0 AND storage_used <= 100),
    timestamp    TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ---------- SERVER MAINTENANCE ----------
CREATE TABLE ServerMaintenance (
    maintenance_id   SERIAL PRIMARY KEY,
    server_id        INTEGER NOT NULL REFERENCES Servers(server_id) ON UPDATE CASCADE ON DELETE CASCADE,
    performed_by     INTEGER REFERENCES Users(user_id),
    maintenance_date TIMESTAMP WITH TIME ZONE NOT NULL,
    description      TEXT,
    status           VARCHAR(50) NOT NULL CHECK (status IN ('scheduled', 'in_progress', 'completed', 'cancelled'))
);

-- ---------- TAGS ----------
CREATE TABLE Tags (
    tag_id   SERIAL PRIMARY KEY,
    tag_name VARCHAR(100) NOT NULL UNIQUE
);

-- ---------- SERVER TAG ASSIGNMENTS ----------
CREATE TABLE ServerTagAssignments (
    server_id INTEGER NOT NULL REFERENCES Servers(server_id) ON UPDATE CASCADE ON DELETE CASCADE,
    tag_id    INTEGER NOT NULL REFERENCES Tags(tag_id) ON UPDATE CASCADE ON DELETE CASCADE,
    PRIMARY KEY (server_id, tag_id)
);

-- ---------- AUDIT LOG ----------
CREATE TABLE AuditLog (
    log_id     SERIAL PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    record_id  INTEGER NOT NULL,
    action     VARCHAR(10) NOT NULL CHECK (action IN ('INSERT', 'UPDATE', 'DELETE')),
    old_value  JSONB,
    new_value  JSONB,
    user_id    INTEGER REFERENCES Users(user_id) ON UPDATE CASCADE ON DELETE SET NULL,
    timestamp  TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ---------- SERVER LOGS ----------
CREATE TABLE ServerLogs (
    log_id        SERIAL PRIMARY KEY,
    server_id     INTEGER NOT NULL REFERENCES Servers(server_id) ON UPDATE CASCADE ON DELETE CASCADE,
    event_type    VARCHAR(50) NOT NULL CHECK(event_type IN ('reboot','error','update','shutdown','startup')),
    description   TEXT,
    severity      VARCHAR(50) NOT NULL CHECK(severity IN ('info','warning','critical')),
    logged_at     TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    performed_by  INTEGER REFERENCES Users(user_id),
    extra_data    JSONB
);

-- ---------- SUPPORT TICKETS ----------
CREATE TABLE SupportTickets (
    ticket_id     SERIAL PRIMARY KEY,
    user_id       INTEGER NOT NULL REFERENCES Users(user_id) ON UPDATE CASCADE ON DELETE CASCADE,
    subject       VARCHAR(200) NOT NULL,
    description   TEXT NOT NULL,
    status        VARCHAR(50) NOT NULL CHECK(status IN ('open','in_progress','resolved','closed')),
    priority      VARCHAR(50) NOT NULL CHECK(priority IN ('low','medium','high','critical')),
    created_at    TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP WITH TIME ZONE
);
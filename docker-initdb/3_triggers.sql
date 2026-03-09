CREATE OR REPLACE FUNCTION get_audit_user_id()
RETURNS INTEGER AS $$
BEGIN
    RETURN NULLIF(current_setting('audit.current_user_id', true), '')::INTEGER;
EXCEPTION
    WHEN OTHERS THEN
        RETURN NULL;
END;
$$ LANGUAGE plpgsql STABLE;


CREATE OR REPLACE FUNCTION audit_trigger_func()
RETURNS TRIGGER AS $$
DECLARE
    v_old_val JSONB;
    v_new_val JSONB;
    v_record_id INTEGER;
BEGIN
    IF TG_OP = 'DELETE' THEN
        v_old_val := to_jsonb(OLD);
        v_new_val := NULL;

        IF TG_TABLE_NAME = 'users' THEN
            v_record_id := OLD.user_id;
        ELSIF TG_TABLE_NAME = 'servers' THEN
            v_record_id := OLD.server_id;
        ELSIF TG_TABLE_NAME = 'servertypes' THEN
            v_record_id := OLD.server_type_id;
        ELSIF TG_TABLE_NAME = 'orders' THEN
            v_record_id := OLD.order_id;
        ELSIF TG_TABLE_NAME = 'payments' THEN
            v_record_id := OLD.payment_id;
        ELSIF TG_TABLE_NAME = 'resourcesusage' THEN
            v_record_id := OLD.usage_id;
        ELSIF TG_TABLE_NAME = 'servermaintenance' THEN
            v_record_id := OLD.maintenance_id;
        ELSIF TG_TABLE_NAME = 'tags' THEN
            v_record_id := OLD.tag_id;
        ELSIF TG_TABLE_NAME = 'servertagassignments' THEN
            v_record_id := OLD.server_id;
        END IF;

    ELSIF TG_OP = 'UPDATE' THEN
        v_old_val := to_jsonb(OLD);
        v_new_val := to_jsonb(NEW);

        IF TG_TABLE_NAME = 'users' THEN
            v_record_id := NEW.user_id;
        ELSIF TG_TABLE_NAME = 'servers' THEN
            v_record_id := NEW.server_id;
        ELSIF TG_TABLE_NAME = 'servertypes' THEN
            v_record_id := NEW.server_type_id;
        ELSIF TG_TABLE_NAME = 'orders' THEN
            v_record_id := NEW.order_id;
        ELSIF TG_TABLE_NAME = 'payments' THEN
            v_record_id := NEW.payment_id;
        ELSIF TG_TABLE_NAME = 'resourcesusage' THEN
            v_record_id := NEW.usage_id;
        ELSIF TG_TABLE_NAME = 'servermaintenance' THEN
            v_record_id := NEW.maintenance_id;
        ELSIF TG_TABLE_NAME = 'tags' THEN
            v_record_id := NEW.tag_id;
        ELSIF TG_TABLE_NAME = 'servertagassignments' THEN
            v_record_id := NEW.server_id;
        END IF;

    ELSIF TG_OP = 'INSERT' THEN
        v_old_val := NULL;
        v_new_val := to_jsonb(NEW);

        IF TG_TABLE_NAME = 'users' THEN
            v_record_id := NEW.user_id;
        ELSIF TG_TABLE_NAME = 'servers' THEN
            v_record_id := NEW.server_id;
        ELSIF TG_TABLE_NAME = 'servertypes' THEN
            v_record_id := NEW.server_type_id;
        ELSIF TG_TABLE_NAME = 'orders' THEN
            v_record_id := NEW.order_id;
        ELSIF TG_TABLE_NAME = 'payments' THEN
            v_record_id := NEW.payment_id;
        ELSIF TG_TABLE_NAME = 'resourcesusage' THEN
            v_record_id := NEW.usage_id;
        ELSIF TG_TABLE_NAME = 'servermaintenance' THEN
            v_record_id := NEW.maintenance_id;
        ELSIF TG_TABLE_NAME = 'tags' THEN
            v_record_id := NEW.tag_id;
        ELSIF TG_TABLE_NAME = 'servertagassignments' THEN
            v_record_id := NEW.server_id;
        END IF;
    END IF;

    INSERT INTO auditlog (table_name, record_id, action, old_value, new_value, user_id, timestamp)
    VALUES (TG_TABLE_NAME, v_record_id, TG_OP, v_old_val, v_new_val, get_audit_user_id(), CURRENT_TIMESTAMP);

    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;

END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION fn_sync_server_status()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'active' THEN
        UPDATE Servers
        SET status = 'rented'
        WHERE server_id = NEW.server_id;
    ELSIF NEW.status IN ('completed', 'cancelled') THEN
        IF NOT EXISTS (
            SELECT 1
            FROM Orders
            WHERE server_id = NEW.server_id
              AND status = 'active'
        ) THEN
            UPDATE Servers
            SET status = 'available'
            WHERE server_id = NEW.server_id
              AND status NOT IN ('offline', 'maintenance');
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER audit_users
    AFTER INSERT OR UPDATE OR DELETE ON users
    FOR EACH ROW EXECUTE PROCEDURE audit_trigger_func();

CREATE TRIGGER audit_servers
    AFTER INSERT OR UPDATE OR DELETE ON servers
    FOR EACH ROW EXECUTE PROCEDURE audit_trigger_func();

CREATE TRIGGER audit_servertypes
    AFTER INSERT OR UPDATE OR DELETE ON servertypes
    FOR EACH ROW EXECUTE PROCEDURE audit_trigger_func();

CREATE TRIGGER audit_orders
    AFTER INSERT OR UPDATE OR DELETE ON orders
    FOR EACH ROW EXECUTE PROCEDURE audit_trigger_func();

CREATE TRIGGER audit_payments
    AFTER INSERT OR UPDATE OR DELETE ON payments
    FOR EACH ROW EXECUTE PROCEDURE audit_trigger_func();

CREATE TRIGGER audit_resourcesusage
    AFTER INSERT OR UPDATE OR DELETE ON resourcesusage
    FOR EACH ROW EXECUTE PROCEDURE audit_trigger_func();

CREATE TRIGGER audit_servermaintenance
    AFTER INSERT OR UPDATE OR DELETE ON servermaintenance
    FOR EACH ROW EXECUTE PROCEDURE audit_trigger_func();

CREATE TRIGGER audit_tags
    AFTER INSERT OR UPDATE OR DELETE ON tags
    FOR EACH ROW EXECUTE PROCEDURE audit_trigger_func();

CREATE TRIGGER audit_servertagassignments
    AFTER INSERT OR UPDATE OR DELETE ON servertagassignments
    FOR EACH ROW EXECUTE PROCEDURE audit_trigger_func();

CREATE TRIGGER trg_sync_server_status
    AFTER INSERT OR UPDATE OF status ON Orders
    FOR EACH ROW EXECUTE FUNCTION fn_sync_server_status();
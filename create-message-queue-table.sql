-- Create device_message_queue table in public schema
-- Run this on your PostgreSQL server (10.0.0.59)
-- 
-- Database structure:
-- - public schema: device_message_queue (new async message queue)
-- - tcasino schema: all existing tables, functions, procedures, views (ported from MSSQL)

-- Connect to postgres database
-- psql -h 10.0.0.59 -U postgres -d postgres

-- Create the device_message_queue table
CREATE TABLE IF NOT EXISTS device_message_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id VARCHAR(255) NOT NULL,
    procedure_name VARCHAR(255) NOT NULL,
    payload JSONB NOT NULL,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW(),
    processed_at TIMESTAMP,
    retry_count INTEGER DEFAULT 0,
    error_message TEXT,
    priority INTEGER DEFAULT 0
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_device_message_queue_device_id 
ON device_message_queue(device_id);

CREATE INDEX IF NOT EXISTS idx_device_message_queue_status 
ON device_message_queue(status);

CREATE INDEX IF NOT EXISTS idx_device_message_queue_created_at 
ON device_message_queue(created_at);

CREATE INDEX IF NOT EXISTS idx_device_message_queue_procedure_name 
ON device_message_queue(procedure_name);

CREATE INDEX IF NOT EXISTS idx_device_message_queue_status_priority 
ON device_message_queue(status, priority DESC, created_at ASC);

-- Create a view for pending messages
CREATE OR REPLACE VIEW pending_device_messages AS
SELECT 
    id,
    device_id,
    procedure_name,
    payload,
    created_at,
    retry_count,
    error_message
FROM device_message_queue 
WHERE status = 'pending'
ORDER BY priority DESC, created_at ASC;

-- Create a function to clean up old processed messages
CREATE OR REPLACE FUNCTION cleanup_old_messages()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM device_message_queue 
    WHERE status IN ('completed', 'failed') 
    AND created_at < NOW() - INTERVAL '7 days';
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Add comments
COMMENT ON TABLE device_message_queue IS 'Queue for asynchronous database operations from gaming devices';
COMMENT ON COLUMN device_message_queue.device_id IS 'MAC address or unique identifier of the gaming device';
COMMENT ON COLUMN device_message_queue.procedure_name IS 'Name of the stored procedure to be executed';
COMMENT ON COLUMN device_message_queue.payload IS 'JSON payload containing procedure parameters and metadata';
COMMENT ON COLUMN device_message_queue.status IS 'Current processing status of the message';
COMMENT ON COLUMN device_message_queue.priority IS 'Processing priority (higher number = higher priority)';

-- Set default search path to include both schemas
-- This ensures both schemas are accessible
ALTER DATABASE postgres SET search_path TO tcasino, public;

-- Verify table creation
SELECT 'device_message_queue table created successfully!' as result;

-- Verify schema setup
SELECT 
    schemaname, 
    tablename 
FROM pg_tables 
WHERE tablename = 'device_message_queue' 
   OR schemaname = 'tcasino'
ORDER BY schemaname, tablename; 
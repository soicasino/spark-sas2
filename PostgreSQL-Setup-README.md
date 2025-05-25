# PostgreSQL Integration for Casino Management System

This document explains how to set up and configure PostgreSQL integration for your casino management application.

## Overview

The application now supports a hybrid database architecture:

- **Synchronous operations** (immediate response needed): Still use direct database calls
- **Asynchronous operations** (logging, monitoring): Use PostgreSQL message queue system
- **Offline capability**: Falls back to SQLite when PostgreSQL is unavailable

## Quick Setup

### 1. Install Dependencies

On your Raspberry Pi, run:

```bash
chmod +x install-postgresql.sh
./install-postgresql.sh
```

### 2. PostgreSQL Server Setup

#### Option A: Local PostgreSQL Installation

If you want to install PostgreSQL on the same Raspberry Pi:

```bash
# Update system
sudo apt update

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### Option B: Remote PostgreSQL Server (Recommended for Production)

If using a remote PostgreSQL server (like `10.0.0.59`):

1. Ensure PostgreSQL server is accessible from your Raspberry Pi
2. Configure PostgreSQL server to accept connections (see Remote Server Configuration below)
3. Only install PostgreSQL client on Raspberry Pi:

```bash
sudo apt install postgresql-client
```

### 3. Set up Database and User

```bash
# Switch to postgres user
sudo -u postgres psql

# Run the setup script (or execute commands manually)
sudo -u postgres psql -f setup-postgresql-database.sql
```

### 4. Create the Message Queue Table

```bash
# Connect to your database
sudo -u postgres psql -d casino_db

# Create the tables and indexes
\i create-postgresql-tables.sql
```

### 5. Configure Connection

The following configuration files have been created with sample values:

| File                 | Sample Value                | Description                     |
| -------------------- | --------------------------- | ------------------------------- |
| `pg_host.ini`        | `10.0.0.59`                 | PostgreSQL server hostname/IP   |
| `pg_database.ini`    | `casino_db`                 | Database name                   |
| `pg_user.ini`        | `casino_user`               | Database username               |
| `pg_password.ini`    | `your_secure_password_here` | Database password               |
| `pg_port.ini`        | `5432`                      | PostgreSQL port                 |
| `pg_schema.ini`      | `tcasino`                   | Schema for existing procedures  |
| `use_postgresql.ini` | `1`                         | Enable PostgreSQL (1=on, 0=off) |

**Important**: Update these files with your actual database credentials!

### 6. Test the Setup

Start your application and check the logs for:

```
PostgreSQL connected successfully
Use PostgreSQL: True
```

## Configuration Details

### Synchronous Operations (Immediate Response Required)

These operations still use direct database calls:

- `tsp_GetBalanceInfoOnGM` - Balance queries
- `tsp_CardRead` / `tsp_CardReadPartial` - Card validation
- `tsp_CheckBillacceptorIn` - Bill acceptance validation
- `tsp_CheckNetwork` - Network connectivity checks
- `tsp_GetCustomerAdditional` - Customer info

### Asynchronous Operations (Message Queue)

These operations are queued for background processing:

- `tsp_InsGameStart` / `tsp_InsGameEnd` - Game logging
- `tsp_InsDeviceMeter` - Meter readings
- `tsp_InsImportantMessage` - General logging
- `tsp_UpdDeviceAdditionalInfo` - Status updates
- `tsp_InsException` - Error logging

## Database Schema Structure

This application uses a two-schema approach in PostgreSQL:

### Schema Layout

- **`public` schema**: Contains the new `device_message_queue` table for async operations
- **`tcasino` schema**: Contains all existing tables, functions, procedures, and views (ported from MSSQL)

### Why Two Schemas?

- **Separation of concerns**: New async functionality is isolated from existing business logic
- **Migration safety**: Existing MSSQL structure is preserved in its own namespace
- **Future flexibility**: Easy to manage and version different parts of the system

## Database Schema

### device_message_queue Table

```sql
CREATE TABLE device_message_queue (
    id UUID PRIMARY KEY,
    device_id VARCHAR(255),           -- Device MAC address
    procedure_name VARCHAR(255),      -- Stored procedure name
    payload JSONB,                    -- Parameters as JSON
    status TEXT DEFAULT 'pending',   -- pending/processing/completed/failed
    created_at TIMESTAMP DEFAULT NOW(),
    processed_at TIMESTAMP,
    retry_count INTEGER DEFAULT 0,
    error_message TEXT,
    priority INTEGER DEFAULT 0
);
```

### Message Payload Example

```json
{
  "procedure_name": "tsp_InsImportantMessage",
  "parameters": ["00:11:22:33:44:55", "Device started", 100, 0, 12345],
  "device_id": "00:11:22:33:44:55",
  "timestamp": "2024-01-15T10:30:00"
}
```

## Remote PostgreSQL Server Configuration

If your PostgreSQL server is on a different machine (like `10.0.0.59`), you need to configure it to accept remote connections:

### 1. Configure PostgreSQL to Accept Connections

On your PostgreSQL server (`10.0.0.59`), edit these files:

#### Edit postgresql.conf

```bash
sudo nano /etc/postgresql/[version]/main/postgresql.conf
```

Find and modify:

```
listen_addresses = '*'          # Allow connections from any IP
# OR specific range:
# listen_addresses = '10.0.0.0/24'
```

#### Edit pg_hba.conf

```bash
sudo nano /etc/postgresql/[version]/main/pg_hba.conf
```

Add this line to allow connections from your Raspberry Pi:

```
# Allow casino app from Raspberry Pi
host    casino_db    casino_user    10.0.0.0/24    md5
```

### 2. Restart PostgreSQL Service

```bash
sudo systemctl restart postgresql
```

### 3. Configure Firewall (if enabled)

```bash
# Allow PostgreSQL port
sudo ufw allow 5432/tcp

# Or allow from specific IP only
sudo ufw allow from 10.0.0.0/24 to any port 5432
```

### 4. Test Remote Connection

From your Raspberry Pi, test the connection:

```bash
# Test connection
psql -h 10.0.0.59 -U casino_user -d casino_db -c "SELECT version();"

# If successful, you should see PostgreSQL version info
```

## Troubleshooting

### Connection Issues

1. Check PostgreSQL service status:

   ```bash
   sudo systemctl status postgresql
   ```

2. Verify database exists:

   ```bash
   sudo -u postgres psql -l
   ```

3. Test connection:

   ```bash
   # For local PostgreSQL
   sudo -u postgres psql -d casino_db -c "SELECT version();"

   # For remote PostgreSQL (10.0.0.59)
   psql -h 10.0.0.59 -U casino_user -d casino_db -c "SELECT version();"
   ```

### Application Logs

Monitor application logs for these messages:

- `PostgreSQL connected successfully` - Connection OK
- `PostgreSQL connection failed: [error]` - Connection problem
- `Queued async message: [procedure]` - Message queued successfully
- `Stored in SQLite fallback: [procedure]` - Offline fallback used

### Fallback Behavior

When PostgreSQL is unavailable:

1. Synchronous operations fall back to MSSQL
2. Asynchronous operations are stored in local SQLite
3. Messages sync to PostgreSQL when connection is restored

## Performance Monitoring

### View Pending Messages

```sql
SELECT * FROM pending_device_messages LIMIT 10;
```

### Check Message Queue Status

```sql
SELECT
    status,
    COUNT(*) as count,
    MIN(created_at) as oldest,
    MAX(created_at) as newest
FROM device_message_queue
GROUP BY status;
```

### Clean Up Old Messages

```sql
SELECT cleanup_old_messages(); -- Removes messages older than 7 days
```

## Security Notes

1. **Change default passwords**: Update `pg_password.ini` with a strong password
2. **Network security**: Configure PostgreSQL to only accept connections from trusted IPs
3. **File permissions**: Secure the `.ini` files with appropriate permissions:
   ```bash
   chmod 600 *.ini
   ```

## Support

If you encounter issues:

1. Check the application logs
2. Verify PostgreSQL service is running
3. Test database connectivity manually
4. Ensure all configuration files have correct values

The system is designed to be resilient - if PostgreSQL is unavailable, the application will continue to work with reduced functionality.

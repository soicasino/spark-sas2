# Windows Setup Guide - Sample Data Generator

## Quick Start for Windows

### Prerequisites

- Windows 10/11
- Python 3.7+ installed
- PostgreSQL server accessible (your server: 10.0.0.59)

### Step 1: Install Dependencies

Choose one of these methods:

#### Method A: PowerShell (Recommended)

```powershell
# Run in PowerShell as regular user (not Administrator)
.\install-postgresql.ps1
```

#### Method B: Command Prompt

```cmd
# Run in Command Prompt
install-postgresql.bat
```

#### Method C: Manual Installation

```cmd
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\activate

# Install PostgreSQL driver
pip install psycopg2-binary

# Install additional dependencies (if requirements file exists)
pip install -r requirements-postgresql.txt
```

### Step 2: Configure Database Connection

Create these configuration files in your project directory:

**pg_host.ini**

```
10.0.0.59
```

**pg_database.ini**

```
postgres
```

**pg_user.ini**

```
postgres
```

**pg_password.ini**

```
s123
```

**pg_port.ini**

```
5432
```

**pg_schema.ini**

```
tcasino
```

**use_postgresql.ini**

```
1
```

### Step 3: Create Database Table

Connect to your PostgreSQL server and run:

```sql
CREATE TABLE device_message_queue (
    id UUID PRIMARY KEY,
    device_id VARCHAR(255),
    procedure_name VARCHAR(255),
    payload JSONB,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW(),
    processed_at TIMESTAMP,
    retry_count INTEGER DEFAULT 0,
    error_message TEXT
);
```

### Step 4: Run Sample Data Generator

#### Method A: Using the Runner Script

```cmd
# Activate virtual environment first
.venv\Scripts\activate

# Run the generator
python run-sample-data-generator.py
```

#### Method B: Direct Execution

```cmd
# Activate virtual environment first
.venv\Scripts\activate

# Run directly
python generate-comprehensive-sample-data.py
```

### Expected Output

```
🚀 Sample Data Generator Runner
========================================
✅ psycopg2 module available
🔄 Executing generate-comprehensive-sample-data.py...
----------------------------------------
🎰 COMPREHENSIVE Device Message Queue Sample Data Generator
============================================================
📋 Based on sql-calls.md documentation
🎯 Generating 10 records per category (80 total)

📊 Configuration: 10.0.0.59:5432 -> postgres
✅ Connected to PostgreSQL

🔄 Generating comprehensive sample data...
✅ Bill Acceptor Operations: 10 samples
✅ Card Operations: 10 samples
✅ Game Operations: 10 samples
✅ Device Status & Monitoring: 10 samples
✅ Customer & Bonus Operations: 10 samples
✅ Financial Operations: 10 samples
✅ Logging & Debugging: 10 samples
✅ Special Edge Cases: 10 samples

📝 Total samples to insert: 80

💾 Inserting samples into device_message_queue...
✅  1/80 - tsp_CheckBillacceptorIn (proc_called)
✅  2/80 - tsp_InsBillAcceptorMoney (completed)
...
✅ 80/80 - tsp_InsException (pending)

📊 FINAL SUMMARY:
   ✅ Successful inserts: 80
   ❌ Failed inserts: 0
   📊 Total records in DB: 80

🎉 Comprehensive sample data generation completed!
```

### Troubleshooting

#### Python Not Found

```cmd
# Check if Python is in PATH
python --version

# If not found, add Python to PATH or use full path
C:\Python39\python.exe --version
```

#### psycopg2 Installation Issues

```cmd
# Try binary version (recommended for Windows)
pip install psycopg2-binary

# If that fails, you may need Visual Studio Build Tools
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
```

#### Connection Issues

- Verify PostgreSQL server is running on 10.0.0.59:5432
- Check firewall settings
- Verify credentials in configuration files
- Test connection with pgAdmin or psql

#### Permission Issues

- Don't run as Administrator
- Ensure you have write permissions in the project directory
- Check if antivirus is blocking Python/pip

### Verify Sample Data

After successful generation, connect to your PostgreSQL database and run:

```sql
-- Check total records
SELECT COUNT(*) FROM device_message_queue;

-- Check status distribution
SELECT status, COUNT(*) FROM device_message_queue GROUP BY status;

-- Check recent records
SELECT device_id, procedure_name, status, created_at
FROM device_message_queue
ORDER BY created_at DESC
LIMIT 10;

-- Check SAS context examples
SELECT
    procedure_name,
    payload->'sas_message'->>'sas_version_id' as sas_version,
    payload->'sas_message'->>'last_sas_command' as last_command
FROM device_message_queue
WHERE payload->'sas_message' IS NOT NULL
LIMIT 5;
```

### Next Steps

1. **Explore the Data**: Use the SQL queries above to explore the generated sample data
2. **Test Your Application**: Use this data to test your casino management system
3. **Modify Parameters**: Edit `generate-comprehensive-sample-data.py` to customize data generation
4. **Add More Data**: Run the generator multiple times to create larger datasets

### File Structure After Setup

```
your-project/
├── .venv/                              # Virtual environment
├── install-postgresql.ps1             # PowerShell installer
├── install-postgresql.bat             # Batch installer
├── generate-comprehensive-sample-data.py  # Main generator
├── run-sample-data-generator.py       # Runner script
├── requirements-postgresql.txt        # Dependencies
├── pg_host.ini                        # Database host
├── pg_database.ini                    # Database name
├── pg_user.ini                        # Database user
├── pg_password.ini                    # Database password
├── pg_port.ini                        # Database port
├── pg_schema.ini                      # Database schema
└── use_postgresql.ini                 # Enable PostgreSQL
```

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Verify all configuration files are created correctly
3. Test PostgreSQL connectivity manually
4. Check Python and pip versions
5. Ensure virtual environment is activated

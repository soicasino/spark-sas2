#!/bin/bash

echo "==============================================="
echo "Installing PostgreSQL dependencies for Casino Management System"
echo "==============================================="

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "Please do not run this script as root"
    exit 1
fi

# Update package lists
echo "[INFO] Updating package lists..."
sudo apt update

# Install PostgreSQL client and development files
echo "[INFO] Installing PostgreSQL client and development packages..."
sudo apt install -y postgresql-client libpq-dev python3-dev

# Install psycopg2 via apt if available (recommended)
echo "[INFO] Attempting to install python3-psycopg2 via apt..."
if sudo apt install -y python3-psycopg2; then
    echo "[INFO] python3-psycopg2 installed successfully via apt."
else
    echo "[WARNING] python3-psycopg2 could not be installed via apt. Will try pip."
fi

# Check if virtual environment exists
if [ -d ".venv" ]; then
    echo "[INFO] Activating existing virtual environment..."
    source .venv/bin/activate
    VENV_PYTHON=".venv/bin/python"
else
    echo "[INFO] Creating virtual environment with system site packages..."
    python3 -m venv .venv --system-site-packages
    source .venv/bin/activate
    VENV_PYTHON=".venv/bin/python"
fi

# Check if psycopg2 is accessible
echo "[INFO] Checking if psycopg2 is accessible..."
if ! "$VENV_PYTHON" -c "import psycopg2" >/dev/null 2>&1; then
    echo "[INFO] psycopg2 not accessible, installing via pip..."
    
    # Try binary version first (no compilation needed)
    if pip install psycopg2-binary; then
        echo "[INFO] psycopg2-binary installed successfully"
    else
        echo "[WARNING] psycopg2-binary failed, trying source version..."
        pip install psycopg2
    fi
else
    echo "[INFO] psycopg2 is already accessible"
fi

# Install additional dependencies
echo "[INFO] Installing additional dependencies..."
pip install -r requirements-postgresql.txt

# Test PostgreSQL connectivity
echo "[INFO] Testing PostgreSQL import..."
if "$VENV_PYTHON" -c "import psycopg2; print('PostgreSQL connectivity ready')"; then
    echo "[SUCCESS] PostgreSQL dependencies installed successfully!"
else
    echo "[ERROR] PostgreSQL dependencies installation failed!"
    exit 1
fi

echo ""
echo "==============================================="
echo "Installation completed!"
echo "==============================================="
echo ""
echo "Next steps:"
echo "1. Create your PostgreSQL database and user"
echo "2. Configure your PostgreSQL connection by creating these files:"
echo "   - pg_host.ini (database host)"
echo "   - pg_database.ini (database name)"
echo "   - pg_user.ini (database user)"
echo "   - pg_password.ini (database password)"
echo "   - use_postgresql.ini (set to '1' to enable)"
echo ""
echo "3. Create the device_message_queue table in your PostgreSQL database:"
echo "   CREATE TABLE device_message_queue ("
echo "     id UUID PRIMARY KEY,"
echo "     device_id VARCHAR(255),"
echo "     procedure_name VARCHAR(255),"
echo "     payload JSONB,"
echo "     status TEXT DEFAULT 'pending',"
echo "     created_at TIMESTAMP DEFAULT NOW(),"
echo "     processed_at TIMESTAMP,"
echo "     retry_count INTEGER DEFAULT 0,"
echo "     error_message TEXT"
echo "   );"
echo ""
echo "4. Restart your application" 
@echo off
setlocal enabledelayedexpansion

echo ===============================================
echo Installing PostgreSQL dependencies for Casino Management System
echo ===============================================

REM Check if Python is installed
echo [INFO] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.7+ from https://python.org
    pause
    exit /b 1
) else (
    for /f "tokens=*" %%i in ('python --version 2^>^&1') do echo [INFO] Found Python: %%i
)

REM Check if pip is available
echo [INFO] Checking pip installation...
pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pip not found. Please ensure pip is installed with Python.
    pause
    exit /b 1
) else (
    for /f "tokens=*" %%i in ('pip --version 2^>^&1') do echo [INFO] Found pip: %%i
)

REM Check if virtual environment exists
if exist ".venv" (
    echo [INFO] Activating existing virtual environment...
    call .venv\Scripts\activate.bat
    set "venvPython=.venv\Scripts\python.exe"
) else (
    echo [INFO] Creating virtual environment...
    python -m venv .venv
    call .venv\Scripts\activate.bat
    set "venvPython=.venv\Scripts\python.exe"
)

REM Upgrade pip in virtual environment
echo [INFO] Upgrading pip in virtual environment...
"%venvPython%" -m pip install --upgrade pip

REM Check if psycopg2 is accessible
echo [INFO] Checking if psycopg2 is accessible...
"%venvPython%" -c "import psycopg2" >nul 2>&1
if errorlevel 1 (
    echo [INFO] psycopg2 not accessible, installing via pip...
    
    REM Try binary version first (no compilation needed)
    echo [INFO] Installing psycopg2-binary (recommended for Windows)...
    pip install psycopg2-binary
    if errorlevel 1 (
        echo [WARNING] psycopg2-binary failed, trying source version...
        echo [INFO] Note: Source version requires Visual Studio Build Tools
        pip install psycopg2
    ) else (
        echo [INFO] psycopg2-binary installed successfully
    )
) else (
    echo [INFO] psycopg2 is already accessible
)

REM Install additional dependencies if requirements file exists
if exist "requirements-postgresql.txt" (
    echo [INFO] Installing additional dependencies from requirements-postgresql.txt...
    pip install -r requirements-postgresql.txt
) else (
    echo [WARNING] requirements-postgresql.txt not found, skipping additional dependencies
)

REM Test PostgreSQL connectivity
echo [INFO] Testing PostgreSQL import...
"%venvPython%" -c "import psycopg2; print('PostgreSQL connectivity ready')" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] PostgreSQL dependencies installation failed!
    pause
    exit /b 1
) else (
    echo [SUCCESS] PostgreSQL dependencies installed successfully!
    "%venvPython%" -c "import psycopg2; print('PostgreSQL connectivity ready')"
)

echo.
echo ===============================================
echo Installation completed!
echo ===============================================
echo.
echo Next steps:
echo 1. Create your PostgreSQL database and user
echo 2. Configure your PostgreSQL connection by creating these files:
echo    - pg_host.ini (database host)
echo    - pg_database.ini (database name)
echo    - pg_user.ini (database user)
echo    - pg_password.ini (database password)
echo    - pg_port.ini (database port)
echo    - pg_schema.ini (database schema)
echo    - use_postgresql.ini (set to '1' to enable)
echo.
echo 3. Create the device_message_queue table in your PostgreSQL database:
echo    CREATE TABLE device_message_queue (
echo      id UUID PRIMARY KEY,
echo      device_id VARCHAR(255),
echo      procedure_name VARCHAR(255),
echo      payload JSONB,
echo      status TEXT DEFAULT 'pending',
echo      created_at TIMESTAMP DEFAULT NOW(),
echo      processed_at TIMESTAMP,
echo      retry_count INTEGER DEFAULT 0,
echo      error_message TEXT
echo    );
echo.
echo 4. Run sample data generator:
echo    python run-sample-data-generator.py
echo.
echo 5. Restart your application
echo.
pause 
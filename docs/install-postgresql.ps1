Write-Host "===============================================" -ForegroundColor Green
Write-Host "Installing PostgreSQL dependencies for Casino Management System" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green

# Check if running as administrator
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if ($currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "[WARNING] Running as Administrator. This is not required for this script." -ForegroundColor Yellow
}

# Check if Python is installed
Write-Host "[INFO] Checking Python installation..." -ForegroundColor Cyan
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[INFO] Found Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python not found. Please install Python 3.7+ from https://python.org" -ForegroundColor Red
    exit 1
}

# Check if pip is available
Write-Host "[INFO] Checking pip installation..." -ForegroundColor Cyan
try {
    $pipVersion = pip --version 2>&1
    Write-Host "[INFO] Found pip: $pipVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] pip not found. Please ensure pip is installed with Python." -ForegroundColor Red
    exit 1
}

# Check if virtual environment exists
if (Test-Path ".venv") {
    Write-Host "[INFO] Activating existing virtual environment..." -ForegroundColor Cyan
    & ".venv\Scripts\Activate.ps1"
    $venvPython = ".venv\Scripts\python.exe"
} else {
    Write-Host "[INFO] Creating virtual environment..." -ForegroundColor Cyan
    python -m venv .venv
    & ".venv\Scripts\Activate.ps1"
    $venvPython = ".venv\Scripts\python.exe"
}

# Upgrade pip in virtual environment
Write-Host "[INFO] Upgrading pip in virtual environment..." -ForegroundColor Cyan
& $venvPython -m pip install --upgrade pip

# Check if psycopg2 is accessible
Write-Host "[INFO] Checking if psycopg2 is accessible..." -ForegroundColor Cyan
$psycopg2Check = & $venvPython -c "import psycopg2" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[INFO] psycopg2 not accessible, installing via pip..." -ForegroundColor Cyan
    
    # Try binary version first (no compilation needed)
    Write-Host "[INFO] Installing psycopg2-binary (recommended for Windows)..." -ForegroundColor Cyan
    pip install psycopg2-binary
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[INFO] psycopg2-binary installed successfully" -ForegroundColor Green
    } else {
        Write-Host "[WARNING] psycopg2-binary failed, trying source version..." -ForegroundColor Yellow
        Write-Host "[INFO] Note: Source version requires Visual Studio Build Tools" -ForegroundColor Yellow
        pip install psycopg2
    }
} else {
    Write-Host "[INFO] psycopg2 is already accessible" -ForegroundColor Green
}

# Install additional dependencies if requirements file exists
if (Test-Path "requirements-postgresql.txt") {
    Write-Host "[INFO] Installing additional dependencies from requirements-postgresql.txt..." -ForegroundColor Cyan
    pip install -r requirements-postgresql.txt
} else {
    Write-Host "[WARNING] requirements-postgresql.txt not found, skipping additional dependencies" -ForegroundColor Yellow
}

# Test PostgreSQL connectivity
Write-Host "[INFO] Testing PostgreSQL import..." -ForegroundColor Cyan
$postgresTest = & $venvPython -c "import psycopg2; print('PostgreSQL connectivity ready')" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "[SUCCESS] PostgreSQL dependencies installed successfully!" -ForegroundColor Green
    Write-Host $postgresTest -ForegroundColor Green
} else {
    Write-Host "[ERROR] PostgreSQL dependencies installation failed!" -ForegroundColor Red
    Write-Host $postgresTest -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "===============================================" -ForegroundColor Green
Write-Host "Installation completed!" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Create your PostgreSQL database and user" -ForegroundColor White
Write-Host "2. Configure your PostgreSQL connection by creating these files:" -ForegroundColor White
Write-Host "   - pg_host.ini (database host)" -ForegroundColor Gray
Write-Host "   - pg_database.ini (database name)" -ForegroundColor Gray
Write-Host "   - pg_user.ini (database user)" -ForegroundColor Gray
Write-Host "   - pg_password.ini (database password)" -ForegroundColor Gray
Write-Host "   - pg_port.ini (database port)" -ForegroundColor Gray
Write-Host "   - pg_schema.ini (database schema)" -ForegroundColor Gray
Write-Host "   - use_postgresql.ini (set to '1' to enable)" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Create the device_message_queue table in your PostgreSQL database:" -ForegroundColor White
Write-Host "   CREATE TABLE device_message_queue (" -ForegroundColor Gray
Write-Host "     id UUID PRIMARY KEY," -ForegroundColor Gray
Write-Host "     device_id VARCHAR(255)," -ForegroundColor Gray
Write-Host "     procedure_name VARCHAR(255)," -ForegroundColor Gray
Write-Host "     payload JSONB," -ForegroundColor Gray
Write-Host "     status TEXT DEFAULT 'pending'," -ForegroundColor Gray
Write-Host "     created_at TIMESTAMP DEFAULT NOW()," -ForegroundColor Gray
Write-Host "     processed_at TIMESTAMP," -ForegroundColor Gray
Write-Host "     retry_count INTEGER DEFAULT 0," -ForegroundColor Gray
Write-Host "     error_message TEXT" -ForegroundColor Gray
Write-Host "   );" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Run sample data generator:" -ForegroundColor White
Write-Host "   python run-sample-data-generator.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "5. Restart your application" -ForegroundColor White 
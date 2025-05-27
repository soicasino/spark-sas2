# PowerShell script for setting up Python environment on Windows 11
# for an application requiring serial, mssql, gui, and web components.

Write-Host "Starting Windows 11 Python environment setup..."
Write-Host "Please ensure Python 3 (specifically a 3.11.x version for this project) is installed."
Write-Host "If you have multiple Python versions, this script will attempt to use 'py -3.11' to create the virtual environment."
Write-Host "You can download Python from https://www.python.org/"
Write-Host "---------------------------------------------------------------------"

# --- 1. Check for Python and Pip ---
# Check if py.exe is available and can find a Python 3.11 installation
$Python311Version = ""
try {
    $Python311Version = (py -3.11 --version 2>&1)
    Write-Host "[INFO] Python 3.11.x version found via 'py.exe': $Python311Version"
}
catch {
    Write-Warning "[WARNING] 'py -3.11 --version' failed. Attempting to use default 'python --version'."
    # Fallback to checking default python if py -3.11 fails
    try {
        $PythonVersion = (python --version 2>&1)
        Write-Host "[INFO] Default Python version found: $PythonVersion"
        if ($PythonVersion -notmatch "Python 3\.11\.") {
            Write-Warning "[WARNING] Default Python is not 3.11.x. The script will try 'py -3.11' for venv creation."
            Write-Warning "[WARNING] If 'py -3.11' also fails later, ensure Python 3.11.x is installed and accessible via the Python Launcher."
        }
    }
    catch {
        Write-Error "[ERROR] No Python installation (neither 'py -3.11' nor 'python') found or accessible. Please install Python 3.11.x and ensure it's in PATH or accessible via 'py.exe'."
        exit 1
    }
}

$PipVersion = ""
try {
    # Try pip with the specific version first if py.exe is available for it
    if ($Python311Version) {
         $PipVersion = (py -3.11 -m pip --version 2>&1)
    } else {
         $PipVersion = (pip --version 2>&1) # Fallback to default pip
    }
    Write-Host "[INFO] Pip version found: $PipVersion"
}
catch {
    Write-Error "[ERROR] pip does not seem to be installed or available. Ensure Python was installed with pip."
    exit 1
}

# --- 2. System-Level Dependencies (Manual Steps Often Required for Some Packages) ---
Write-Host ""
Write-Host "[INFO] Checking for system-level dependencies (manual steps might be needed):"

# For pymssql (Microsoft SQL Server connection)
Write-Host "[INFO] For 'pymssql' to connect to SQL Server, you need the Microsoft ODBC Driver for SQL Server."
Write-Host "[INFO] If not already installed, download and install it from the Microsoft website."
Write-Host "[INFO] Search for 'Download ODBC Driver for SQL Server'."
Write-Host "[INFO] After installation, ensure it's configured in your ODBC Data Sources (odbcad32.exe)."

# For pywebview and wxPython (HTML GUI)
Write-Host "[INFO] For 'pywebview', ensure you have a compatible web rendering engine."
Write-Host "[INFO] On Windows 10/11, this is typically Microsoft Edge WebView2."
Write-Host "[INFO] If pywebview has issues, you might need to install/update the WebView2 runtime."
Write-Host "[INFO] Search for 'Download Edge WebView2 Runtime'."
Write-Host "[INFO] For 'wxPython' and 'cefpython3', you may need Visual C++ Redistributable."
Write-Host "[INFO] If installation fails, install Microsoft Visual C++ Redistributable (latest)."

# --- 3. Create Python Virtual Environment (if it doesn't exist) ---
$VenvDir = ".venv"
Write-Host ""
if (-not (Test-Path -Path $VenvDir -PathType Container)) {
    Write-Host "[INFO] Creating Python virtual environment in '$VenvDir' using Python 3.11..."
    try {
        # Use py.exe to specify Python 3.11 for venv creation
        py -3.11 -m venv $VenvDir
        Write-Host "[INFO] Virtual environment created successfully with Python 3.11.x."
    }
    catch {
        Write-Error "[ERROR] Failed to create virtual environment with 'py -3.11'. Error: $_"
        Write-Error "[ERROR] Please ensure Python 3.11.x is installed and accessible via the Python Launcher ('py.exe')."
        exit 1
    }
} else {
    Write-Host "[INFO] Virtual environment '$VenvDir' already exists."
    Write-Host "[INFO] Note: If it was created with a different Python version, you might want to delete and recreate it."
}

# --- 4. Activate Virtual Environment and Install Python Packages ---
# Activation in PowerShell is done by running the Activate.ps1 script.
# For this script, we will call pip from within the venv directly.
$PipPath = Join-Path -Path $VenvDir -ChildPath "Scripts\pip.exe"
$PythonPath = Join-Path -Path $VenvDir -ChildPath "Scripts\python.exe"

if (-not (Test-Path $PipPath)) {
    Write-Error "[ERROR] pip not found in virtual environment: $PipPath. Please ensure the venv was created correctly with Python 3.11."
    exit 1
}

Write-Host ""
Write-Host "[INFO] Upgrading pip in the virtual environment..."
try {
    & $PipPath install --upgrade pip
    Write-Host "[INFO] pip upgraded successfully."
}
catch {
    Write-Warning "[WARNING] Failed to upgrade pip. Continuing with existing version. $_"
}

Write-Host ""
Write-Host "[INFO] Installing/Upgrading Cython in the virtual environment (often a build dependency)..."
try {
    & $PipPath install --upgrade cython
    Write-Host "[INFO] Cython installed/upgraded successfully."
}
catch {
    Write-Warning "[WARNING] Failed to install/upgrade Cython. Some packages might fail to build if they need it. $_"
}

Write-Host ""
Write-Host "[INFO] Installing required Python packages into the virtual environment..."
Write-Host "[INFO] This may take some time, especially for packages that need compilation."

$packages = @(
    "pyserial",
    "crccheck",
    "psutil",
    # "distro", # distro is Linux-specific, not typically needed on Windows for this type of app
    "pymssql",
    "pywebview",
    "PyQt5",    # PyQt5 usually installs from a wheel on Windows
    "wxpython",  # For HTML GUI support
    "cefpython3", # For CEF browser support
    "Flask",
    "flask-restful"
)

foreach ($package in $packages) {
    Write-Host "[INFO] Installing $package..."
    try {
        & $PipPath install $package
        Write-Host "[INFO] Successfully installed $package."
    }
    catch {
        Write-Error "[ERROR] Failed to install $package. Error: $($_.Exception.Message)"
        Write-Warning "[WARNING] Please check the error message. You might need to install additional system libraries or C++ Build Tools if a package requires compilation."
        Write-Warning "[WARNING] For C++ Build Tools, visit: https://visualstudio.microsoft.com/visual-cpp-build-tools/"
    }
}

Write-Host ""
Write-Host "[INFO] Python package installation attempt complete."
Write-Host "---------------------------------------------------------------------"
Write-Host "Setup script finished."
Write-Host "To activate the virtual environment in your current PowerShell session, run:"
Write-Host "  .\$VenvDir\Scripts\Activate.ps1"
Write-Host "If you are using Command Prompt (cmd.exe), run:"
Write-Host "  $VenvDir\Scripts\activate.bat"
Write-Host ""
Write-Host "After activation, you can run your Python script, e.g.:"
Write-Host "  python your_script_name.py"
Write-Host "To deactivate (from PowerShell or CMD), simply type 'deactivate'."
Write-Host "---------------------------------------------------------------------"

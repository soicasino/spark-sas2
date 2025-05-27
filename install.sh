#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e
# Treat unset variables as an error when substituting.
set -u
# Cause a pipeline to return the exit status of the last command in the pipe
# that returned a non-zero status.
set -o pipefail

echo "Starting Raspberry Pi Python environment setup for your SAS application..."
echo "This script will install dependencies for SAS protocol communication, GUI (PyQt5),"
echo "database connectivity (PostgreSQL, MS SQL Server), and web services (Flask)."

# --- 1. Update System Package List ---
echo ""
echo "[INFO] Updating system package list..."
sudo apt update

# --- 2. Install System-Level Dependencies ---
echo ""
echo "[INFO] Installing system-level dependencies..."

# For PyQt5 (GUI)
echo "[INFO] Ensuring Qt5 development tools and PyQt5 system components are installed..."
sudo apt install -y qt5-qmake qtbase5-dev python3-pyqt5.sip libqt5svg5-dev python3-pyqt5

# For pymssql (Microsoft SQL Server connection)
echo "[INFO] Ensuring FreeTDS development files (build dependency for pymssql if built from source) are installed..."
sudo apt install -y freetds-dev
echo "[INFO] Attempting to install python3-pymssql via apt..."
if sudo apt install -y python3-pymssql; then
    echo "[INFO] python3-pymssql installed successfully via apt."
else
    echo "[WARNING] python3-pymssql could not be installed via apt. The script will later try pip, which might fail."
fi

# For PostgreSQL (database connection)
echo "[INFO] Installing PostgreSQL client libraries and development files..."
sudo apt install -y postgresql-client libpq-dev python3-psycopg2
echo "[INFO] Attempting to install python3-psycopg2 via apt..."
if sudo apt install -y python3-psycopg2; then
    echo "[INFO] python3-psycopg2 installed successfully via apt."
else
    echo "[WARNING] python3-psycopg2 could not be installed via apt. The script will later try pip."
fi

# For pywebview and wxPython (HTML GUI support)
echo "[INFO] Ensuring system dependencies for wxPython and HTML GUI are installed..."
sudo apt install -y python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-webkit2-4.0 libgtk-3-dev
# For wxPython dependencies
sudo apt install -y libgtk-3-dev libwebkitgtk-3.0-dev libwxgtk3.0-gtk3-dev

echo "[INFO] System dependencies installation attempt complete."

# --- 3. Create Python Virtual Environment ---
VENV_DIR=".venv"
PYTHON_EXEC="python3" # Assuming python3 is the desired interpreter

# Force removal of existing .venv directory to ensure a clean start with correct flags
if [ -d "$VENV_DIR" ]; then
    echo ""
    echo "[INFO] Removing existing virtual environment directory: '$VENV_DIR'..."
    # Ensure the user running this script has permission to remove .venv, or run script with sudo
    # Be cautious with rm -rf; ensure VENV_DIR is correctly set.
    if [ "$VENV_DIR" == ".venv" ]; then # Basic safety check
        sudo rm -rf "$VENV_DIR" # Use sudo if the venv was created by root or needs root to remove
        echo "[INFO] Existing virtual environment removed."
    else
        echo "[ERROR] VENV_DIR is not '.venv'. Aborting removal for safety."
        exit 1
    fi
fi

echo ""
echo "[INFO] Creating Python virtual environment in '$VENV_DIR' with access to system site-packages..."
# Added --system-site-packages to allow access to apt-installed python3-pymssql and python3-pyqt5
$PYTHON_EXEC -m venv --system-site-packages "$VENV_DIR"
echo "[INFO] Virtual environment created."


# --- 4. Activate Virtual Environment and Install Python Packages ---
echo ""
echo "[INFO] Activating virtual environment and installing Python packages..."

VENV_PIP="$VENV_DIR/bin/pip"
VENV_PYTHON="$VENV_DIR/bin/python"

echo "[INFO] Upgrading pip in the virtual environment..."
"$VENV_PIP" install --upgrade pip

echo "[INFO] Installing/Upgrading Cython in the virtual environment (build dependency for some packages)..."
"$VENV_PIP" install --upgrade cython

echo "[INFO] Installing required Python packages into the virtual environment..."
# PyQt5 and pymssql should ideally be picked up from the system install if `python3-pyqt5` and `python3-pymssql`
# were successfully installed by apt AND the venv has access to system-site-packages.

PACKAGES_TO_INSTALL="pyserial crccheck psutil distro pywebview Flask flask-restful psycopg2-binary wxpython cefpython3"

# Check if python3-pymssql is accessible. If not, and apt didn't install it, add to pip list.
# This check assumes the venv (with --system-site-packages) makes apt-installed packages importable.
if ! "$VENV_PYTHON" -c "import pymssql" >/dev/null 2>&1; then
    if ! dpkg -s python3-pymssql >/dev/null 2>&1; then # Check if apt actually installed it
        echo "[INFO] python3-pymssql was not found via apt and is not accessible in venv. Adding pymssql to pip install list (might fail to build)."
        PACKAGES_TO_INSTALL="$PACKAGES_TO_INSTALL pymssql" # This will likely fail as before if apt version is not available/working
    else
        echo "[WARNING] python3-pymssql is installed via apt, but still not accessible in the virtual environment created with --system-site-packages. This is unexpected."
        echo "[WARNING] You might need to ensure your Python3 and pip versions are consistent or troubleshoot venv creation."
        # Optionally, still try to pip install it as a last resort, though it's likely to fail.
        # PACKAGES_TO_INSTALL="$PACKAGES_TO_INSTALL pymssql"
    fi
else
    echo "[INFO] pymssql is accessible in the virtual environment (likely from system site-packages via apt)."
fi

# Check for PyQt5 similarly if issues persist, though python3-pyqt5 from apt is usually reliable with --system-site-packages
if ! "$VENV_PYTHON" -c "from PyQt5 import QtCore" >/dev/null 2>&1; then
    if ! dpkg -s python3-pyqt5 >/dev/null 2>&1; then
        echo "[INFO] python3-pyqt5 was not found via apt and is not accessible in venv. Adding PyQt5 to pip install list (might fail to build or take very long)."
        PACKAGES_TO_INSTALL="$PACKAGES_TO_INSTALL PyQt5"
    else
        echo "[WARNING] python3-pyqt5 is installed via apt, but still not accessible in the virtual environment created with --system-site-packages. This is unexpected."
        # PACKAGES_TO_INSTALL="$PACKAGES_TO_INSTALL PyQt5" # Fallback, likely to be slow/fail
    fi
else
    echo "[INFO] PyQt5 is accessible in the virtual environment (likely from system site-packages via apt)."
fi

# Check for psycopg2 (PostgreSQL adapter)
if ! "$VENV_PYTHON" -c "import psycopg2" >/dev/null 2>&1; then
    if ! dpkg -s python3-psycopg2 >/dev/null 2>&1; then
        echo "[INFO] python3-psycopg2 was not found via apt and is not accessible in venv. psycopg2-binary is already in pip install list."
    else
        echo "[WARNING] python3-psycopg2 is installed via apt, but still not accessible in the virtual environment created with --system-site-packages."
    fi
else
    echo "[INFO] psycopg2 is accessible in the virtual environment (likely from system site-packages via apt)."
    # Remove psycopg2-binary from pip install list since system package is working
    PACKAGES_TO_INSTALL=$(echo "$PACKAGES_TO_INSTALL" | sed 's/psycopg2-binary//g')
fi


echo "[INFO] Installing Python packages: $PACKAGES_TO_INSTALL"
"$VENV_PIP" install $PACKAGES_TO_INSTALL

echo ""
echo "[INFO] Python package installation attempt complete."
echo ""
echo "---------------------------------------------------------------------"
echo "Setup script finished."
echo "To activate the virtual environment in your current terminal session, run:"
echo "  source $VENV_DIR/bin/activate"
echo "After activation, you can run your Python script, e.g.:"
echo "  python your_script_name.py"
echo "To deactivate, simply type 'deactivate'."
echo "---------------------------------------------------------------------"


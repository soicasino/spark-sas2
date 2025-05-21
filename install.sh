#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e
# Treat unset variables as an error when substituting.
set -u
# Cause a pipeline to return the exit status of the last command in the pipe
# that returned a non-zero status.
set -o pipefail

echo "Starting Raspberry Pi Python environment setup for your SAS application..."

# --- 1. Update System Package List ---
echo ""
echo "[INFO] Updating system package list..."
sudo apt update

# --- 2. Install System-Level Dependencies ---
echo ""
echo "[INFO] Installing system-level dependencies..."

# For PyQt5 (GUI) - Assuming it's already installed via apt as per previous steps.
# If not, or to ensure it is:
echo "[INFO] Ensuring Qt5 development tools and PyQt5 system components are installed..."
sudo apt install -y qt5-qmake qtbase5-dev python3-pyqt5.sip libqt5svg5-dev python3-pyqt5

# For pymssql (Microsoft SQL Server connection)
echo "[INFO] Ensuring FreeTDS development files for pymssql are installed..."
sudo apt install -y freetds-dev

# For pywebview (if needed, though not explicitly in the pip list from the error log)
# echo "[INFO] Ensuring system dependencies for pywebview are installed..."
# sudo apt install -y python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-webkit2-4.0 libgtk-3-dev

echo "[INFO] System dependencies installation attempt complete."

# --- 3. Create Python Virtual Environment (if it doesn't exist) ---
VENV_DIR=".venv"
PYTHON_EXEC="python3" # Assuming python3 is the desired interpreter

if [ ! -d "$VENV_DIR" ]; then
    echo ""
    echo "[INFO] Creating Python virtual environment in '$VENV_DIR'..."
    $PYTHON_EXEC -m venv "$VENV_DIR"
    echo "[INFO] Virtual environment created."
else
    echo ""
    echo "[INFO] Virtual environment '$VENV_DIR' already exists."
fi

# --- 4. Activate Virtual Environment and Install Python Packages ---
echo ""
echo "[INFO] Activating virtual environment and installing Python packages..."

VENV_PIP="$VENV_DIR/bin/pip"
VENV_PYTHON="$VENV_DIR/bin/python"

echo "[INFO] Upgrading pip in the virtual environment..."
"$VENV_PIP" install --upgrade pip

echo "[INFO] Installing/Upgrading Cython in the virtual environment (needed for pymssql)..."
"$VENV_PIP" install --upgrade cython

echo "[INFO] Installing required Python packages into the virtual environment..."

# Install pymssql separately, trying an older version first
echo "[INFO] Attempting to install a compatible version of pymssql (e.g., <2.3.0)..."
if "$VENV_PIP" install "pymssql<2.3.0" ; then
    echo "[INFO] pymssql installed successfully."
else
    echo "[WARNING] Failed to install pymssql with version <2.3.0. You might need to troubleshoot pymssql installation further."
    echo "[WARNING] Check for errors related to FreeTDS or compiler issues."
fi

echo "[INFO] Installing other Python packages..."
# Note: PyQt5 should be picked up from the system install if `python3-pyqt5` was successfully installed by apt.
"$VENV_PIP" install pyserial crccheck psutil distro pywebview Flask flask-restful

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


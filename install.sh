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

# For PyQt5 (GUI)
echo "[INFO] Installing Qt5 development tools and PyQt5 system components..."
sudo apt install -y qt5-qmake qtbase5-dev python3-pyqt5.sip libqt5svg5-dev python3-pyqt5

# For pymssql (Microsoft SQL Server connection)
echo "[INFO] Installing FreeTDS development files for pymssql..."
sudo apt install -y freetds-dev

# For RPi.GPIO (if your script uses it directly, though not in the pip list you provided)
# echo "[INFO] Installing RPi.GPIO (if needed by the script)..."
# sudo apt install -y python3-rpi.gpio

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

# Source the activate script to run subsequent commands within the venv
# This is tricky in a script because `source` affects the current shell.
# We'll run pip commands by explicitly calling the venv's pip.
VENV_PIP="$VENV_DIR/bin/pip"
VENV_PYTHON="$VENV_DIR/bin/python"

echo "[INFO] Upgrading pip in the virtual environment..."
"$VENV_PIP" install --upgrade pip

echo "[INFO] Installing/Upgrading Cython in the virtual environment (needed for pymssql)..."
"$VENV_PIP" install --upgrade cython

echo "[INFO] Installing required Python packages into the virtual environment..."
# Note: PyQt5 should be picked up from the system install if `python3-pyqt5` was successfully installed by apt.
# If pip tries to build PyQt5 here and fails, it indicates the apt version isn't being used by the venv's Python,
# which can sometimes happen if the venv was created with certain flags or if system site-packages are not accessible.
# However, typically, system-installed packages for the Python version used to create the venv are available.
"$VENV_PIP" install pyserial crccheck psutil distro pymssql pywebview Flask flask-restful

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


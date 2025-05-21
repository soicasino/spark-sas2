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

# For pywebview (if needed)
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

echo "[INFO] Installing/Upgrading Cython in the virtual environment (build dependency for some packages)..."
"$VENV_PIP" install --upgrade cython

echo "[INFO] Installing required Python packages into the virtual environment..."
# PyQt5 and pymssql should ideally be picked up from the system install if `python3-pyqt5` and `python3-pymssql`
# were successfully installed by apt.
# We will not explicitly try to pip install pymssql if the apt install was successful.
# If apt install of python3-pymssql failed, pip might still try and likely fail for the same reasons.

PACKAGES_TO_INSTALL="pyserial crccheck psutil distro pywebview Flask flask-restful"

# Check if python3-pymssql was installed by apt. If not, add pymssql to pip list as a fallback.
if ! dpkg -s python3-pymssql >/dev/null 2>&1; then
    echo "[INFO] python3-pymssql was not found via apt. Adding pymssql to pip install list (might fail to build)."
    PACKAGES_TO_INSTALL="$PACKAGES_TO_INSTALL pymssql"
else
    echo "[INFO] python3-pymssql is installed via apt, skipping pip install for pymssql."
fi


echo "[INFO] Installing other Python packages: $PACKAGES_TO_INSTALL"
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


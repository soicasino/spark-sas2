#!/bin/bash

# Wrapper script for systemd to start the Spark SAS2 service
# This ensures proper virtual environment activation and path resolution

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the project directory
cd "$SCRIPT_DIR"

# Activate virtual environment
source .venv/bin/activate

# Set environment variables
export PATH="$SCRIPT_DIR/.venv/bin:$PATH"
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

# Start the application
exec uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1 
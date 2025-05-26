#!/usr/bin/env python3
"""
Raspberry Pi Application Runner
Alternative Python script to run the main application
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_colored(message, color_code):
    """Print colored messages to terminal"""
    print(f"\033[{color_code}m{message}\033[0m")

def print_success(message):
    print_colored(message, "0;32")  # Green

def print_warning(message):
    print_colored(message, "1;33")  # Yellow

def print_error(message):
    print_colored(message, "0;31")  # Red

def check_environment():
    """Check if we're running on the right environment"""
    if not platform.system() == "Linux":
        print_warning("Warning: This script is designed for Linux/Raspberry Pi")
    
    # Check if we're in the right directory
    current_dir = Path.cwd()
    app_file = current_dir / "raspberryPython3.py"
    venv_dir = current_dir / ".venv"
    
    if not app_file.exists():
        print_error("Error: raspberryPython3.py not found in current directory!")
        return False
    
    if not venv_dir.exists():
        print_error("Error: .venv directory not found!")
        print_warning("Please create a virtual environment first:")
        print("python3 -m venv .venv")
        return False
    
    return True

def activate_venv_and_run():
    """Activate virtual environment and run the application"""
    try:
        # Set environment variables
        os.environ["DISPLAY"] = ":0.0"
        
        # Get the virtual environment python path
        venv_python = Path.cwd() / ".venv" / "bin" / "python3"
        
        if not venv_python.exists():
            print_error("Error: Python executable not found in virtual environment!")
            return False
        
        print_success("Starting Python application with virtual environment...")
        print_warning(f"Running: {venv_python} raspberryPython3.py")
        
        # Run the application
        result = subprocess.run([str(venv_python), "raspberryPython3.py"], 
                              cwd=Path.cwd())
        
        if result.returncode == 0:
            print_success("Application completed successfully.")
        else:
            print_error(f"Application exited with error code: {result.returncode}")
        
        return result.returncode == 0
        
    except Exception as e:
        print_error(f"Error running application: {e}")
        return False

def main():
    """Main function"""
    print_success("Starting Raspberry Pi Application Runner...")
    
    if not check_environment():
        sys.exit(1)
    
    success = activate_venv_and_run()
    
    if success:
        print_success("Runner completed successfully.")
        sys.exit(0)
    else:
        print_error("Runner completed with errors.")
        sys.exit(1)

if __name__ == "__main__":
    main() 
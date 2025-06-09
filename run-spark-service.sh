#!/bin/bash

# Raspberry Pi Application Runner Script (Service Mode)
# This script runs the Python application in the background using nohup or screen

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

PID_FILE="$SCRIPT_DIR/spark-sas2.pid"
LOG_FILE="$SCRIPT_DIR/spark-sas2.log"

# Function to check if service is running
is_running() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0
        else
            rm -f "$PID_FILE"
            return 1
        fi
    fi
    return 1
}

# Function to start the service
start_service() {
    print_step "Starting Spark SAS2 service..."
    
    # Check if already running
    if is_running; then
        local pid=$(cat "$PID_FILE")
        print_warning "Service is already running (PID: $pid)"
        return 1
    fi
    
    # Check if virtual environment exists
    if [ ! -d ".venv" ]; then
        print_error "Virtual environment (.venv) not found!"
        print_warning "Please run the install script first or create venv manually"
        return 1
    fi
    
    # Check if Python application exists
    if [ ! -f "main.py" ]; then
        print_error "main.py not found!"
        return 1
    fi
    
    # Activate virtual environment
    print_status "Activating virtual environment..."
    source .venv/bin/activate
    
    # Check if activation was successful
    if [ "$VIRTUAL_ENV" = "" ]; then
        print_error "Failed to activate virtual environment!"
        return 1
    fi
    
    # Install/update requirements if requirements file exists
    if [ -f "requirements.txt" ]; then
        print_status "Installing/updating requirements..."
        pip install -r requirements.txt > /dev/null 2>&1
    fi
    
    # Start the application in background
    print_status "Starting application in background..."
    print_status "Log file: $LOG_FILE"
    
    # Set environment variables
    export DISPLAY=:0.0
    export PYTHONUNBUFFERED=1
    
    # Start with nohup and redirect output to log file
    nohup python main.py > "$LOG_FILE" 2>&1 &
    local pid=$!
    
    # Save PID to file
    echo "$pid" > "$PID_FILE"
    
    # Wait a moment and check if process is still running
    sleep 2
    if ps -p "$pid" > /dev/null 2>&1; then
        print_status "Service started successfully (PID: $pid)"
        print_status "View logs with: tail -f $LOG_FILE"
        return 0
    else
        print_error "Service failed to start"
        rm -f "$PID_FILE"
        return 1
    fi
}

# Function to stop the service
stop_service() {
    print_step "Stopping Spark SAS2 service..."
    
    if ! is_running; then
        print_warning "Service is not running"
        return 1
    fi
    
    local pid=$(cat "$PID_FILE")
    print_status "Stopping service (PID: $pid)..."
    
    # Try graceful shutdown first
    kill "$pid"
    
    # Wait up to 10 seconds for graceful shutdown
    local count=0
    while [ $count -lt 10 ] && ps -p "$pid" > /dev/null 2>&1; do
        sleep 1
        count=$((count + 1))
    done
    
    # Force kill if still running
    if ps -p "$pid" > /dev/null 2>&1; then
        print_warning "Graceful shutdown failed, forcing kill..."
        kill -9 "$pid"
        sleep 1
    fi
    
    # Clean up PID file
    rm -f "$PID_FILE"
    
    if ! ps -p "$pid" > /dev/null 2>&1; then
        print_status "Service stopped successfully"
        return 0
    else
        print_error "Failed to stop service"
        return 1
    fi
}

# Function to restart the service
restart_service() {
    print_step "Restarting Spark SAS2 service..."
    stop_service
    sleep 2
    start_service
}

# Function to show service status
show_status() {
    print_step "Spark SAS2 Service Status"
    
    if is_running; then
        local pid=$(cat "$PID_FILE")
        print_status "Service is running (PID: $pid)"
        
        # Show process details
        echo "Process details:"
        ps -p "$pid" -o pid,ppid,cmd,etime,pcpu,pmem
        
        # Show log tail if log file exists
        if [ -f "$LOG_FILE" ]; then
            echo
            print_status "Recent log entries:"
            tail -10 "$LOG_FILE"
        fi
    else
        print_warning "Service is not running"
        
        # Show last few log entries if available
        if [ -f "$LOG_FILE" ]; then
            echo
            print_status "Last log entries:"
            tail -10 "$LOG_FILE"
        fi
    fi
}

# Function to show logs
show_logs() {
    if [ -f "$LOG_FILE" ]; then
        if [ "$1" = "-f" ]; then
            print_status "Following log file (Ctrl+C to exit)..."
            tail -f "$LOG_FILE"
        else
            print_status "Showing log file:"
            cat "$LOG_FILE"
        fi
    else
        print_warning "Log file not found: $LOG_FILE"
    fi
}

# Function to show usage
show_usage() {
    echo "Usage: $0 {start|stop|restart|status|logs|logs -f}"
    echo
    echo "Commands:"
    echo "  start    - Start the service in background"
    echo "  stop     - Stop the running service"
    echo "  restart  - Restart the service"
    echo "  status   - Show service status and recent logs"
    echo "  logs     - Show all logs"
    echo "  logs -f  - Follow logs in real-time"
    echo
    echo "Files:"
    echo "  PID file: $PID_FILE"
    echo "  Log file: $LOG_FILE"
}

# Main script logic
case "$1" in
    start)
        start_service
        ;;
    stop)
        stop_service
        ;;
    restart)
        restart_service
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs "$2"
        ;;
    *)
        show_usage
        exit 1
        ;;
esac

exit $? 
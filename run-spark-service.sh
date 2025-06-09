#!/bin/bash

# Service Management Script for Spark SAS2
# Usage: ./run-spark-service.sh [start|stop|restart|status|logs|install]

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SERVICE_NAME="spark-sas2"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Function to print usage
print_usage() {
    echo -e "${BLUE}Spark SAS2 Service Manager${NC}"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo -e "  ${GREEN}start${NC}     - Start the SAS service"
    echo -e "  ${GREEN}stop${NC}      - Stop the SAS service"
    echo -e "  ${GREEN}restart${NC}   - Restart the SAS service"
    echo -e "  ${GREEN}status${NC}    - Show service status"
    echo -e "  ${GREEN}logs${NC}      - Show service logs (real-time)"
    echo -e "  ${GREEN}logs -f${NC}   - Follow logs in real-time"
    echo -e "  ${GREEN}install${NC}   - Install the systemd service"
    echo -e "  ${GREEN}uninstall${NC} - Remove the systemd service"
    echo ""
}

# Function to check if service exists
check_service_exists() {
    if ! systemctl list-unit-files | grep -q "^${SERVICE_NAME}.service"; then
        echo -e "${RED}❌ Service '${SERVICE_NAME}' is not installed${NC}"
        echo -e "${YELLOW}💡 Run: $0 install${NC}"
        return 1
    fi
    return 0
}

# Function to start service
start_service() {
    echo -e "${YELLOW}🚀 Starting ${SERVICE_NAME} service...${NC}"
    
    if check_service_exists; then
        sudo systemctl start $SERVICE_NAME
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Service started successfully${NC}"
            sleep 2
            show_status
        else
            echo -e "${RED}❌ Failed to start service${NC}"
            return 1
        fi
    fi
}

# Function to stop service
stop_service() {
    echo -e "${YELLOW}🛑 Stopping ${SERVICE_NAME} service...${NC}"
    
    if check_service_exists; then
        sudo systemctl stop $SERVICE_NAME
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Service stopped successfully${NC}"
        else
            echo -e "${RED}❌ Failed to stop service${NC}"
            return 1
        fi
    fi
}

# Function to restart service
restart_service() {
    echo -e "${YELLOW}🔄 Restarting ${SERVICE_NAME} service...${NC}"
    
    if check_service_exists; then
        sudo systemctl restart $SERVICE_NAME
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Service restarted successfully${NC}"
            sleep 2
            show_status
        else
            echo -e "${RED}❌ Failed to restart service${NC}"
            return 1
        fi
    fi
}

# Function to show service status
show_status() {
    if check_service_exists; then
        echo -e "${BLUE}📊 Service Status:${NC}"
        sudo systemctl status $SERVICE_NAME --no-pager -l
        echo ""
        echo -e "${BLUE}🌐 API Endpoints:${NC}"
        echo "  Main API: http://localhost:8000"
        echo "  Documentation: http://localhost:8000/docs" 
        echo "  WebSocket: ws://localhost:8000/ws/live-updates"
    fi
}

# Function to show logs
show_logs() {
    if check_service_exists; then
        if [ "$2" = "-f" ] || [ "$2" = "--follow" ]; then
            echo -e "${BLUE}📋 Following logs (Ctrl+C to stop):${NC}"
            sudo journalctl -u $SERVICE_NAME -f --no-pager
        else
            echo -e "${BLUE}📋 Recent logs:${NC}"
            sudo journalctl -u $SERVICE_NAME --no-pager -l --since "10 minutes ago"
            echo ""
            echo -e "${YELLOW}💡 Use '$0 logs -f' to follow logs in real-time${NC}"
        fi
    fi
}

# Function to install service
install_service() {
    echo -e "${YELLOW}📦 Installing ${SERVICE_NAME} service...${NC}"
    
    if [ -f "${SCRIPT_DIR}/create-service.sh" ]; then
        cd "$SCRIPT_DIR"
        chmod +x create-service.sh
        sudo ./create-service.sh
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Service installed successfully${NC}"
            echo -e "${YELLOW}💡 Use '$0 start' to start the service${NC}"
        else
            echo -e "${RED}❌ Failed to install service${NC}"
            return 1
        fi
    else
        echo -e "${RED}❌ create-service.sh not found in ${SCRIPT_DIR}${NC}"
        return 1
    fi
}

# Function to uninstall service
uninstall_service() {
    echo -e "${YELLOW}🗑️  Uninstalling ${SERVICE_NAME} service...${NC}"
    
    if check_service_exists; then
        # Stop service first
        sudo systemctl stop $SERVICE_NAME 2>/dev/null
        
        # Disable service
        sudo systemctl disable $SERVICE_NAME
        
        # Remove service file
        sudo rm -f "/etc/systemd/system/${SERVICE_NAME}.service"
        
        # Reload systemd
        sudo systemctl daemon-reload
        
        echo -e "${GREEN}✅ Service uninstalled successfully${NC}"
    fi
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
        show_logs "$@"
        ;;
    install)
        install_service
        ;;
    uninstall)
        uninstall_service
        ;;
    "")
        print_usage
        exit 1
        ;;
    *)
        echo -e "${RED}❌ Unknown command: $1${NC}"
        echo ""
        print_usage
        exit 1
        ;;
esac 
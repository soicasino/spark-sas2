import time

print("port_manager.py loaded")

class PortManager:
    """Port detection and management"""
    
    def __init__(self):
        self.available_ports = []

    def find_ports_linux(self):
        """Find available ports on Linux - FIXED to find actual serial ports"""
        self.available_ports = []
        
        # Check for USB serial ports
        try:
            import glob
            usb_ports = glob.glob('/dev/ttyUSB*')
            for port in usb_ports:
                self.available_ports.append({
                    'port_no': port,
                    'is_used': False,
                    'device_name': ''
                })
            print(f"Found USB ports: {usb_ports}")
        except Exception as e:
            print(f"Error finding USB ports: {e}")
        
        # Check for ACM ports (USB serial adapters)
        try:
            import glob
            acm_ports = glob.glob('/dev/ttyACM*')
            for port in acm_ports:
                self.available_ports.append({
                    'port_no': port,
                    'is_used': False,
                    'device_name': ''
                })
            print(f"Found ACM ports: {acm_ports}")
        except Exception as e:
            print(f"Error finding ACM ports: {e}")
        
        # Check for standard serial ports
        try:
            import glob
            serial_ports = glob.glob('/dev/ttyS*')
            # Only add first few serial ports to avoid testing too many
            for port in serial_ports[:4]:  # Limit to first 4 serial ports
                self.available_ports.append({
                    'port_no': port,
                    'is_used': False,
                    'device_name': ''
                })
            print(f"Found serial ports: {serial_ports[:4]}")
        except Exception as e:
            print(f"Error finding serial ports: {e}")
        
        # Alternative method using pyserial if available
        if not self.available_ports:
            try:
                import serial.tools.list_ports
                ports = serial.tools.list_ports.comports()
                for port in ports:
                    self.available_ports.append({
                        'port_no': port.device,
                        'is_used': False,
                        'device_name': f"{port.description}"
                    })
                print(f"Found ports via pyserial: {[p.device for p in ports]}")
            except Exception as e:
                print(f"Error using pyserial port detection: {e}")
        
        # If still no ports found, add some common defaults to test
        if not self.available_ports:
            print("No serial ports detected. Adding common defaults to test...")
            common_ports = ['/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyACM0', '/dev/ttyS0']
            for port in common_ports:
                self.available_ports.append({
                    'port_no': port,
                    'is_used': False,
                    'device_name': 'default'
                })
        
        print(f"Total ports to test: {len(self.available_ports)}")
        for port in self.available_ports:
            print(f"  - {port['port_no']}")
            
        return self.available_ports

    def find_sas_port(self, config):
        """Find SAS port by testing communication - like working code's FindPortForSAS"""
        print("<FIND SAS PORT>-----------------------------------------------------------------")
        
        if not self.available_ports:
            self.find_ports_linux()
            
        for port_info in self.available_ports:
            if not port_info['is_used']:
                port_name = port_info['port_no']
                print(f"Testing SAS on port: {port_name}")
                
                # Try different device types like working code
                for device_type in [8, 1, 2]:  # Try default first, then Novomatic types
                    config.config.set('machine', 'devicetypeid', str(device_type))
                    
                    from sas_communicator import SASCommunicator
                    sas_comm = SASCommunicator(port_name, config)
                    if sas_comm.open_port():
                        print(f"Port {port_name} opened, testing communication...")
                        
                        # Test communication
                        found_sas = False
                        for attempt in range(10):  # 10 attempts like working code
                            sas_comm.request_sas_version()
                            time.sleep(0.1)
                            
                            response = sas_comm.get_data_from_sas_port()
                            if response and ("0154" in response or len(response) > 6):
                                print(f"SAS found on port {port_name} with device type {device_type}")
                                found_sas = True
                                break
                                
                            time.sleep(0.05)
                        
                        sas_comm.close_port()
                        
                        if found_sas:
                            port_info['is_used'] = True
                            port_info['device_name'] = 'sas'
                            print("</FIND SAS PORT>-----------------------------------------------------------------")
                            return port_name, device_type
                            
                print(f"No SAS found on port {port_name}")
        
        print("No SAS port found!")
        print("</FIND SAS PORT>-----------------------------------------------------------------")
        return None, None

    def get_all_ports(self):
        """Return all available ports for use by other components like card reader"""
        if not self.available_ports:
            self.find_ports_linux()
        return self.available_ports 
import threading
import time
from config_manager import ConfigManager
from port_manager import PortManager
from sas_communicator import SASCommunicator

class SlotMachineApplication:
    """Main application - simplified for SAS communication testing"""
    
    def __init__(self):
        self.config = ConfigManager()
        self.port_mgr = PortManager()
        self.sas_comm = None
        self.running = False
        self.sas_poll_timer = None

    def check_system_info(self):
        """Check system and available ports"""
        print("=== SYSTEM CHECK ===")
        
        # Check if we're running as root (needed for serial ports)
        import os
        print(f"Running as user: {os.getuid()} (0=root)")
        
        # Check for serial devices
        print("\nChecking for serial devices:")
        import glob
        
        dev_files = glob.glob('/dev/tty*')
        print(f"All /dev/tty* devices: {len(dev_files)}")
        
        usb_files = glob.glob('/dev/ttyUSB*')
        print(f"USB serial devices: {usb_files}")
        
        acm_files = glob.glob('/dev/ttyACM*')
        print(f"ACM serial devices: {acm_files}")
        
        s_files = glob.glob('/dev/ttyS*')
        print(f"Standard serial devices: {s_files[:5]}...")  # Show first 5
        
        # Check permissions
        for port in usb_files + acm_files + s_files[:2]:
            try:
                import stat
                st = os.stat(port)
                mode = stat.filemode(st.st_mode)
                print(f"  {port}: {mode}")
            except:
                print(f"  {port}: Cannot access")
        
        # Try pyserial detection
        try:
            import serial.tools.list_ports
            ports = list(serial.tools.list_ports.comports())
            print(f"\nPySerial detected ports:")
            for port in ports:
                print(f"  {port.device}: {port.description}")
        except Exception as e:
            print(f"\nPySerial detection failed: {e}")
        
        print("=== END SYSTEM CHECK ===\n")

    def initialize_sas(self):
        """Initialize SAS communication"""
        print("Initializing SAS communication...")
        
        # First check system
        self.check_system_info()
        
        # Find SAS port
        sas_port, device_type = self.port_mgr.find_sas_port(self.config)
        
        if sas_port:
            print(f"Using SAS port: {sas_port}, device type: {device_type}")
            self.config.config.set('machine', 'devicetypeid', str(device_type))
            
            self.sas_comm = SASCommunicator(sas_port, self.config)
            if self.sas_comm.open_port():
                print("SAS communication initialized successfully!")
                # --- Card reader integration in a separate thread ---
                if hasattr(self.port_mgr, 'get_all_ports'):
                    port_list = self.port_mgr.get_all_ports()
                else:
                    port_list = []  # TODO: Implement get_all_ports in PortManager to return port info dicts
                # Ensure /dev/ttyUSB0 is included BEFORE starting the thread
                if not any(p.get('port_no') == '/dev/ttyUSB0' or p.get('port') == '/dev/ttyUSB0' for p in port_list):
                    port_list.append({'port_no': '/dev/ttyUSB0', 'is_used': 0, 'device_name': ''})
                print(f"[DEBUG] Port list for card reader: {port_list}")
                self.card_reader_thread = threading.Thread(
                    target=self.card_reader_thread_main, args=(port_list,), daemon=True)
                print("[Main] Starting card reader thread...")
                self.card_reader_thread.start()
                # --- End card reader integration ---
                return True
            else:
                print("Failed to open SAS port")
                return False
        else:
            print("No SAS port found")
            return False

    def card_reader_thread_main(self, port_list):
        print("[CardReaderThread] Card reader thread started.")
        self.sas_comm.find_ports_and_read_card_if_present(port_list)
        print("[CardReaderThread] Card reader thread finished.")

    def sas_polling_loop(self):
        """SAS polling loop"""
        if not self.running or not self.sas_comm or not self.sas_comm.is_port_open:
            return
        
        # Send poll
        self.sas_comm.send_general_poll()
        
        # Check for response
        time.sleep(0.05)  # Give time for response
        response = self.sas_comm.get_data_from_sas_port()
        if response:
            self.sas_comm.handle_received_sas_command(response)
        
        # Schedule next poll
        if self.running:
            self.sas_poll_timer = threading.Timer(0.04, self.sas_polling_loop)  # 40ms like working code
            self.sas_poll_timer.daemon = True
            self.sas_poll_timer.start()

    def test_sas_commands(self):
        """Test basic SAS commands"""
        if not self.sas_comm:
            print("SAS not initialized")
            return
            
        print("Testing SAS commands...")
        
        # Test SAS version
        print("Requesting SAS version...")
        self.sas_comm.request_sas_version()
        time.sleep(0.2)
        response = self.sas_comm.get_data_from_sas_port()
        if response:
            self.sas_comm.handle_received_sas_command(response)
        
        time.sleep(1)
        
        # Test balance query
        print("Requesting balance info...")
        self.sas_comm.request_balance_info()
        time.sleep(0.2)
        response = self.sas_comm.get_data_from_sas_port()
        if response:
            self.sas_comm.handle_received_sas_command(response)

    def start(self):
        """Start the application"""
        print("Starting Slot Machine Application...")
        
        if not self.initialize_sas():
            print("Failed to initialize SAS. Exiting.")
            return
        
        self.running = True
        
        # Test some commands
        self.test_sas_commands()
        
        # Start polling
        self.sas_polling_loop()
        
        print("Application started. Press Ctrl+C to exit.")
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Shutdown requested.")
        finally:
            self.shutdown()

    def shutdown(self):
        """Shutdown the application"""
        print("Shutting down...")
        self.running = False
        
        if self.sas_poll_timer:
            self.sas_poll_timer.cancel()
        
        if self.sas_comm:
            self.sas_comm.close_port()
        
        print("Shutdown complete.") 
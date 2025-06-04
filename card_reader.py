import serial
import time
import platform

class CardReader:
    def __init__(self):
        self.serial_port = None
        self.port_name = None
        self.is_port_open = False
        self.is_card_reader_found = False
        self.card_reader_interval = 0.05  # Default for Fuheng/Eject
        self.last_card_number = None

    def find_port(self, port_list):
        """
        Try to find and open the card reader port from a list of candidate port names.
        Sets self.serial_port and self.port_name if successful.
        """
        for port_info in port_list:
            if port_info.get('is_used', 0) != 0:
                continue
            port_name = port_info['port_no'] if 'port_no' in port_info else port_info.get('port')
            try:
                ser = serial.Serial()
                ser.port = port_name
                ser.baudrate = 9600
                ser.bytesize = serial.EIGHTBITS
                ser.parity = serial.PARITY_NONE
                ser.stopbits = serial.STOPBITS_ONE
                ser.timeout = 0.2
                ser.open()
                print(f"Trying card reader port: {port_name}")
                # Try to send a card reader command and check for response
                if self._test_card_reader(ser):
                    self.serial_port = ser
                    self.port_name = port_name
                    self.is_port_open = True
                    self.is_card_reader_found = True
                    port_info['is_used'] = 1
                    port_info['device_name'] = 'cardreader'
                    print(f"Card reader found and opened on port: {port_name}")
                    return True
                else:
                    ser.close()
            except Exception as e:
                print(f"Error opening/testing card reader port {port_name}: {e}")
        print("No card reader found.")
        return False

    def _test_card_reader(self, ser):
        """
        Send a test command to the card reader and check for a valid response.
        Returns True if the card reader responds as expected.
        """
        try:
            # Typical card reader poll command (from ref):
            test_cmd = bytearray.fromhex("02000235310307")
            ser.write(test_cmd)
            time.sleep(self.card_reader_interval)
            retry = 5
            while retry > 0:
                if ser.in_waiting > 0:
                    resp = ser.read(ser.in_waiting)
                    if resp:
                        # Accept any non-empty response as valid for now
                        return True
                time.sleep(0.02)
                retry -= 1
        except Exception as e:
            print(f"Error testing card reader: {e}")
        return False

    def read_card(self):
        """
        Send the card read command and parse the card number from the response.
        Prints the card number if found.
        """
        if not self.is_port_open or not self.serial_port:
            print("Card reader port not open.")
            return None
        try:
            cmd = bytearray.fromhex("02000235310307")
            self.serial_port.write(cmd)
            time.sleep(self.card_reader_interval)
            retry = 5
            tdata = b''
            while retry > 0:
                if self.serial_port.in_waiting > 0:
                    tdata += self.serial_port.read(self.serial_port.in_waiting)
                else:
                    retry -= 1
                    time.sleep(0.02)
                    continue
                if tdata:
                    break
            if not tdata:
                print("No response from card reader.")
                return None
            hex_data = tdata.hex().upper()
            print(f"Raw card reader response: {hex_data}")
            # Parse card number (example logic, may need adjustment)
            if hex_data.startswith("020007"):  # Typical card data response
                # Card number is usually 8 hex chars after a marker (e.g. '353159')
                idx = hex_data.find("353159")
                if idx != -1:
                    card_no = hex_data[idx+6:idx+14]
                    print(f"Card number: {card_no}")
                    self.last_card_number = card_no
                    return card_no
            print("Card number not found in response.")
            return None
        except Exception as e:
            print(f"Error reading card: {e}")
            return None

    def card_eject(self):
        """
        Send the card eject command to the card reader to eject the card.
        """
        if not self.is_port_open or not self.serial_port:
            print("Card reader port not open.")
            return False
        try:
            eject_cmd = bytearray.fromhex("02000232300301")
            self.serial_port.write(eject_cmd)
            time.sleep(self.card_reader_interval)
            print(f"Card eject command sent on port: {self.port_name}")
            return True
        except Exception as e:
            print(f"Error sending card eject command: {e}")
            return False

    def close(self):
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            self.is_port_open = False
            print(f"Card reader port {self.port_name} closed.")

    def send_command(self, hex_string):
        """
        Send a generic hex command to the card reader.
        Returns True if sent successfully, False otherwise.
        """
        if not self.is_port_open or not self.serial_port:
            print("Card reader port not open.")
            return False
        try:
            cmd = bytearray.fromhex(hex_string)
            self.serial_port.write(cmd)
            time.sleep(self.card_reader_interval)
            print(f"Sent command to card reader on port {self.port_name}: {hex_string}")
            return True
        except Exception as e:
            print(f"Error sending command to card reader: {e}")
            return False

    def set_led_color(self, hex_string):
        """
        Send a command to set the card reader's LED/color (hex string required by hardware).
        """
        print(f"Setting card reader LED/color with command: {hex_string}")
        return self.send_command(hex_string) 
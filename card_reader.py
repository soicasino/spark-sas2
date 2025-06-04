import serial
import time
import threading
import platform

class CardReader:
    def __init__(self):
        self.serial_port = serial.Serial()
        self.port_name = None
        self.is_card_reader_opened = False
        self.is_card_inside = False
        self.card_reader_interval = 0.05
        self.polling_thread = None
        self.polling_active = False
        self.last_card_number = None

    def find_port(self, port_list):
        """
        Try to find and open the card reader port from a list of candidate port names.
        Sets self.serial_port and self.port_name if successful.
        """
        print("[CardReaderScan] Starting card reader port scan...")
        self.is_card_reader_opened = False
        for port_info in port_list:
            if port_info.get('is_used', 0) != 0 or self.is_card_reader_opened:
                print(f"[CardReaderScan] Skipping port (already used): {port_info.get('port_no', port_info.get('port'))}")
                continue
            port_name = port_info['port_no'] if 'port_no' in port_info else port_info.get('port')
            print(f"[CardReaderScan] Trying port: {port_name}")
            try:
                print(f"[CardReaderScan] Setting serial params: baudrate=9600, bytesize=8, parity=NONE, stopbits=1, timeout=0.2")
                self.serial_port.port = port_name
                self.serial_port.baudrate = 9600
                self.serial_port.bytesize = serial.EIGHTBITS
                self.serial_port.parity = serial.PARITY_NONE
                self.serial_port.stopbits = serial.STOPBITS_ONE
                self.serial_port.timeout = 0.2
                self.serial_port.open()
                print(f"[CardReaderScan] Port opened: {port_name}")
                time.sleep(self.card_reader_interval)
                if self._wait_for_card_reader_opened():
                    self.port_name = port_name
                    self.is_card_reader_opened = True
                    port_info['is_used'] = 1
                    port_info['device_name'] = 'cardreader'
                    print(f"[CardReaderScan] Card reader found and opened on port: {port_name}")
                    print(f"[CardReaderScan] Marked port as used: {port_name}")
                    self._send_poll_command()  # Initial poll
                    break
                else:
                    self.serial_port.close()
                    print(f"[CardReaderScan] Port closed (not card reader): {port_name}")
            except Exception as e:
                print(f"[CardReaderScan] Exception on port {port_name}: {e}")
        if not self.is_card_reader_opened:
            print("[CardReaderScan] No card reader found after scanning all ports.")
        else:
            print(f"[CardReaderScan] Card reader scan complete. Found on port: {self.port_name}")
        return self.is_card_reader_opened

    def _send_poll_command(self):
        try:
            poll_cmd = bytearray.fromhex("02000235310307")
            self.serial_port.write(poll_cmd)
        except Exception as e:
            print(f"Error sending poll command: {e}")

    def _wait_for_card_reader_opened(self):
        retry = 10
        while retry > 0:
            self._send_poll_command()
            time.sleep(self.card_reader_interval)
            if self.serial_port.in_waiting > 0:
                resp = self.serial_port.read(self.serial_port.in_waiting)
                if resp and (b"06" in resp or len(resp) > 0):
                    print("Card reader responded.")
                    return True
            retry -= 1
        return False

    def start_polling(self):
        if not self.is_card_reader_opened:
            print("Card reader not opened, cannot start polling.")
            return
        if self.polling_thread and self.polling_thread.is_alive():
            print("Polling already running.")
            return
        self.polling_active = True
        self.polling_thread = threading.Thread(target=self._poll_card_reader, daemon=True)
        self.polling_thread.start()
        print("Card reader polling started.")

    def stop_polling(self):
        self.polling_active = False
        if self.polling_thread:
            self.polling_thread.join(timeout=1)
            print("Card reader polling stopped.")

    def _poll_card_reader(self):
        while self.polling_active:
            try:
                # Always send poll command (or special command if queued)
                poll_cmd = "02000235310307"
                send_cmd = poll_cmd
                # (Special command queue logic can be added here if needed)
                print("[CardReaderRead] Polling for card...")
                self._send_command_hex(send_cmd)
                time.sleep(self.card_reader_interval)
                tdata = ""
                retry = 5
                # Read response
                while True:
                    if self.serial_port.in_waiting == 0:
                        retry -= 1
                        if retry <= 0:
                            break
                        time.sleep(0.02)
                        continue
                    out = b''
                    while self.serial_port.in_waiting > 0:
                        out += self.serial_port.read(1)
                    if not out:
                        continue
                    tdata += out.hex().upper()
                if tdata:
                    print(f"[CardReaderRead] Raw response: {tdata}")
                    # If ACK (06), send ENQ (05) and wait for next response
                    if tdata == "06":
                        print("[CardReaderRead] Received ACK, sending ENQ...")
                        self._send_command_hex("05")
                        tdata = ""
                        retry = 20
                        while True:
                            if self.serial_port.in_waiting == 0:
                                retry -= 1
                                if retry <= 0:
                                    break
                                time.sleep(0.05)
                                continue
                            out = b''
                            while self.serial_port.in_waiting > 0:
                                out += self.serial_port.read(1)
                            if not out:
                                continue
                            tdata += out.hex().upper()
                        if tdata:
                            print(f"[CardReaderRead] Raw response: {tdata}")
                    # Now check for card data
                    if tdata.startswith("020007"):
                        idx = tdata.find("353159")
                        if idx != -1:
                            card_no = tdata[idx+6:idx+14]
                            if card_no != self.last_card_number:
                                print(f"[CardReaderRead] Card detected: {card_no}")
                                self.last_card_number = card_no
                                self.is_card_inside = True
                    else:
                        self.is_card_inside = False
            except Exception as e:
                print(f"[rCloud] Polling error: {e}")
            time.sleep(self.card_reader_interval)

    def _send_command_hex(self, hex_string):
        try:
            cmd = bytearray.fromhex(hex_string)
            self.serial_port.write(cmd)
        except Exception as e:
            print(f"[rCloud] Error sending command: {e}")

    def card_eject(self):
        if not self.is_card_reader_opened:
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
            print(f"Card reader port {self.port_name} closed.")
        self.is_card_reader_opened = False
        self.polling_active = False

    def send_command(self, hex_string):
        """
        Send a generic hex command to the card reader.
        Returns True if sent successfully, False otherwise.
        """
        if not self.is_card_reader_opened:
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
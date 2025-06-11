import serial
import time
import threading
import asyncio
from datetime import datetime, timedelta

class CardReader:
    """
    An improved CardReader class with a state machine to handle
    transient communication errors and prevent false 'card removed' events.
    """
    def __init__(self):
        # --- Configuration ---
        self.serial_port = serial.Serial()
        self.port_name = None
        self.card_reader_interval = 0.1  # Normal polling interval (seconds)
        self.recovery_interval = 0.05    # Faster polling during recovery (seconds)
        self.recovery_duration = timedelta(seconds=2.0)  # How long to try recovery

        # --- State Management ---
        self.polling_active = False
        self.polling_thread = None
        self.is_card_reader_opened = False
        self.last_card_number = None

        # State machine states
        self.STATE_NO_CARD = "NO_CARD"
        self.STATE_CARD_PRESENT = "CARD_PRESENT"
        self.STATE_COMM_LOST = "COMM_LOST"
        self.current_state = self.STATE_NO_CARD

        self.comm_lost_time = None

        # Legacy compatibility
        self.is_card_inside = False  # For compatibility with existing code

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
        """Starts the background polling thread."""
        if not self.is_card_reader_opened:
            print("Card reader not opened, cannot start polling.")
            return
        if self.polling_thread and self.polling_thread.is_alive():
            print("Polling already running.")
            return
        self.polling_active = True
        self.polling_thread = threading.Thread(target=self._polling_loop, daemon=True)
        self.polling_thread.start()
        print("Card reader polling started.")

    def stop_polling(self):
        """Stops the background polling thread."""
        self.polling_active = False
        if self.polling_thread:
            self.polling_thread.join(timeout=1)
            print("Card reader polling stopped.")

    def _send_command_hex(self, hex_string):
        """Sends a command to the serial port."""
        try:
            cmd = bytearray.fromhex(hex_string)
            self.serial_port.write(cmd)
            return True
        except Exception as e:
            print(f"[CardReader] Error sending command: {e}")
            return False

    def _read_response(self):
        """Reads a response from the serial port with enhanced protocol handling."""
        try:
            time.sleep(self.card_reader_interval)
            tdata = ""
            retry = 5
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
                if tdata == "06":
                    # Handle ACK response - send ENQ
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
            
            return tdata
        except Exception as e:
            print(f"[CardReader] Error reading response: {e}")
            return None

    def _extract_card_number(self, tdata):
        """
        Extracts the card number from the raw hex response.
        Adjust this logic if your card reader protocol changes.
        """
        if tdata and tdata.startswith("020007"):
            idx = tdata.find("353159")
            if idx != -1:
                return tdata[idx+6:idx+14]
        return None

    def _handle_successful_poll(self, card_number):
        """Handles the logic for a successful poll that detects a card."""
        if self.current_state == self.STATE_NO_CARD:
            # --- State Transition: NO_CARD -> CARD_PRESENT ---
            self.last_card_number = card_number
            self.current_state = self.STATE_CARD_PRESENT
            self.is_card_inside = True  # Legacy compatibility
            print(f"[CardReader] State: {self.current_state}. Card inserted: {card_number}")
            self._broadcast_card_event("card_inserted", card_number)
        
        elif self.current_state == self.STATE_COMM_LOST:
            # --- State Transition: COMM_LOST -> CARD_PRESENT ---
            elapsed = datetime.now() - self.comm_lost_time if self.comm_lost_time else timedelta(0)
            print(f"[CardReader] State: COMM_LOST -> CARD_PRESENT. Communication restored for card {self.last_card_number} after {elapsed.total_seconds():.1f}s.")
            self.current_state = self.STATE_CARD_PRESENT
            self.comm_lost_time = None
        
        # If already in CARD_PRESENT and same card, do nothing (normal operation)

    def _handle_failed_poll(self):
        """Handles the logic for a poll that does not detect a card."""
        if self.current_state == self.STATE_CARD_PRESENT:
            # --- State Transition: CARD_PRESENT -> COMM_LOST ---
            self.current_state = self.STATE_COMM_LOST
            self.comm_lost_time = datetime.now()
            print(f"[CardReader] State: CARD_PRESENT -> COMM_LOST. Communication lost with card {self.last_card_number}. Starting recovery...")

        elif self.current_state == self.STATE_COMM_LOST:
            # --- Check for Timeout in COMM_LOST state ---
            elapsed = datetime.now() - self.comm_lost_time
            if elapsed > self.recovery_duration:
                # --- State Transition: COMM_LOST -> NO_CARD (Confirmed Removal) ---
                ejected_card = self.last_card_number
                print(f"[CardReader] State: COMM_LOST -> NO_CARD. Recovery timed out after {elapsed.total_seconds():.1f}s. Card removed: {ejected_card}")
                self.current_state = self.STATE_NO_CARD
                self.last_card_number = None
                self.is_card_inside = False  # Legacy compatibility
                self.comm_lost_time = None
                self._broadcast_card_event("card_removed", ejected_card)
            else:
                # Still in recovery period
                remaining = self.recovery_duration - elapsed
                if int(remaining.total_seconds() * 10) % 10 == 0:  # Log every 0.1s during recovery
                    print(f"[CardReader] Recovery in progress... {remaining.total_seconds():.1f}s remaining")
        
        # If already in NO_CARD, do nothing.

    def _polling_loop(self):
        """The main loop for polling the card reader."""
        while self.polling_active:
            # Determine polling interval based on state
            interval = self.recovery_interval if self.current_state == self.STATE_COMM_LOST else self.card_reader_interval
            
            # Send the poll command
            if self._send_command_hex("02000235310307"):
                response = self._read_response()
                card_number = self._extract_card_number(response) if response else None

                if card_number:
                    self._handle_successful_poll(card_number)
                else:
                    self._handle_failed_poll()
            else:
                # Command send failed - treat as failed poll
                self._handle_failed_poll()
            
            time.sleep(interval)

    def _broadcast_card_event(self, event_type: str, card_number: str):
        """Broadcast card events via WebSocket (non-blocking)"""
        try:
            # Create a new event loop in a separate thread if needed
            def broadcast_async():
                try:
                    # Try to get the current event loop
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # If we're in an async context, schedule the coroutine
                        asyncio.create_task(self._send_websocket_event(event_type, card_number))
                    else:
                        # If no loop is running, run the coroutine
                        loop.run_until_complete(self._send_websocket_event(event_type, card_number))
                except RuntimeError:
                    # No event loop in current thread, create one
                    asyncio.run(self._send_websocket_event(event_type, card_number))
                except Exception as e:
                    print(f"[CardReader] Error broadcasting card event: {e}")
            
            # Run in a separate thread to avoid blocking
            thread = threading.Thread(target=broadcast_async, daemon=True)
            thread.start()
            
        except Exception as e:
            print(f"[CardReader] Error starting broadcast thread: {e}")

    async def _send_websocket_event(self, event_type: str, card_number: str):
        """Send WebSocket event for card insertion/removal"""
        try:
            from websocket_manager import connection_manager
            
            formatted_display = {
                "event": f"🎴 Card {'Inserted' if event_type == 'card_inserted' else 'Removed'}",
                "card_number": card_number if card_number else "Unknown",
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "status": "🟢 Active" if event_type == "card_inserted" else "🔴 Removed"
            }
            
            await connection_manager.broadcast_to_subscribed("card_events", {
                "event_type": event_type,
                "card_number": card_number,
                "formatted_display": formatted_display,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            print(f"[CardReader] Error sending WebSocket event: {e}")

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
        """Stops polling and closes the serial port."""
        self.stop_polling()
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            print(f"Card reader port {self.port_name} closed.")
        self.is_card_reader_opened = False

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
import threading
import time
from card_reader import CardReader

class CardReaderManager:
    def __init__(self, port_list, card_reader_type=2):
        self.port_list = port_list
        self.card_reader_type = card_reader_type
        self.card_reader = None
        self.thread = None
        self.running = False

    def start(self):
        if self.thread and self.thread.is_alive():
            print("[CardReaderManager] Thread already running.")
            return
        self.running = True
        self.thread = threading.Thread(target=self._thread_main, daemon=True)
        print("[CardReaderManager] Starting card reader manager thread...")
        self.thread.start()

    def stop(self):
        self.running = False
        if self.card_reader:
            self.card_reader.stop_polling()
            self.card_reader.close()
        if self.thread:
            self.thread.join(timeout=2)
            print("[CardReaderManager] Card reader manager thread stopped.")

    def _thread_main(self):
        print("[CardReaderManager] Thread started. Scanning for card reader...")
        self.card_reader = CardReader()
        # Optionally set interval/type here if needed
        if self.card_reader_type == 1:
            self.card_reader.card_reader_interval = 0.5
        else:
            self.card_reader.card_reader_interval = 0.05
        found = self.card_reader.find_port(self.port_list)
        if found:
            print(f"[CardReaderManager] Card reader found on port: {self.card_reader.port_name}")
            # Immediately check for card after opening
            self.card_reader._send_command_hex("02000235310307")
            time.sleep(self.card_reader.card_reader_interval)
            if self.card_reader.serial_port.in_waiting > 0:
                resp = self.card_reader.serial_port.read(self.card_reader.serial_port.in_waiting)
                hex_data = resp.hex().upper()
                if hex_data.startswith("020007"):
                    idx = hex_data.find("353159")
                    if idx != -1:
                        card_no = hex_data[idx+6:idx+14]
                        print(f"[CardReaderManager] Card detected immediately after open: {card_no}")
                        self.card_reader.last_card_number = card_no
                        self.card_reader.is_card_inside = True
            self.card_reader.start_polling()
            while self.running:
                time.sleep(0.5)
            print("[CardReaderManager] Stopping card reader polling...")
            self.card_reader.stop_polling()
            self.card_reader.close()
        else:
            print("[CardReaderManager] No card reader found. Thread exiting.") 
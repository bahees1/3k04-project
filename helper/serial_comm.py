# Serial Comm
import serial
import struct
import time

class PacemakerSerial:
    def __init__(self, port="COM7", baud=115200):
        self.port = port
        self.baud = baud
        self.ser = None

    def connect(self):
        print("\n=== CONNECT PACEMAKER ===")
        print(f"Attempting to connect to {self.port} @ {self.baud}...")

        try:
            self.ser = serial.Serial(self.port, self.baud, timeout=1)
            print("SUCCESS: Serial connected.\n")
            return True
        except Exception as e:
            print("FAILED: Serial Error:", e, "\n")
            return False

    def close(self):
        if self.ser:
            print("Closing serial connection.")
            self.ser.close()

    def send_packet(self, param_dict):
        """
        DEBUG VERSION — prints EVERYTHING happening during packet formation and send.
        """
        print("\n==============================")
        print("BUILDING PACKET IN serial_comm")
        print("==============================")

        PACKET_ORDER = [
            "Reserved0", "Reserved1", "Reserved2",
            "mode",
            "Lower Rate Limit",
            "Upper Rate Limit",
            "Maximum Sensor Rate",
            "Atrial Amplitude",
            "Ventricular Amplitude",
            "Atrial Pulse Width",
            "Ventricular Pulse Width",
            "Atrial Sensitivity",
            "Ventricular Sensitivity",
            "VRP",
            "ARP",
            "ActivityThreshold",
            "ReactionTime",
            "ResponseFactor",
            "RecoveryTime"
        ]

        packet_bytes = []

        for key in PACKET_ORDER:
            print(f"\nProcessing field: {key}")

            if key.startswith("Reserved"):
                byte_val = 0
                print(f"  -> Reserved, using 0")

            elif key == "mode":
                byte_val = param_dict.get("mode", 0)
                print(f"  -> mode = {byte_val}")

            elif key == "ActivityThreshold":
                byte_val = param_dict.get("ActivityThreshold", 0)
                print(f"  -> ActivityThreshold = {byte_val}")

            else:
                raw = param_dict.get(key, 0)
                print(f"  -> Raw value from param_dict: {raw}")

                try:
                    byte_val = int(raw) & 0xFF
                    print(f"     Converted to byte: {byte_val} (0x{byte_val:02X})")
                except Exception as e:
                    print(f"     ERROR converting '{raw}': {e}")
                    byte_val = 0

            packet_bytes.append(byte_val)

        # ONLY FIRST 18 BYTES
        packet_bytes = packet_bytes[:18]

        print("\nFINAL PACKET (DEC):")
        print(packet_bytes)

        print("\nFINAL PACKET (HEX):")
        print([f"0x{b:02X}" for b in packet_bytes])
        print("\nPreparing to pack...")

        packet = struct.pack(f"{len(packet_bytes)}B", *packet_bytes)

        if not self.ser or not self.ser.is_open:
            print("ERROR: Serial not connected. Cannot send packet.\n")
            return

        print("\n=== SENDING PACKET OVER SERIAL ===")
        try:
            bytes_written = self.ser.write(packet)
            self.ser.flush()

            print(f"Bytes written: {bytes_written}")
            print("Packet sent successfully.")

            # Give MCU time
            time.sleep(0.05)

            # Check if pacemaker MCU responds
            if self.ser.in_waiting > 0:
                resp = self.ser.read(self.ser.in_waiting)
                print("RESPONSE RECEIVED:", list(resp))
                print("RESPONSE HEX:", [f"0x{b:02X}" for b in resp])
            else:
                print("No response received from pacemaker.")

        except Exception as e:
            print("ERROR WHILE SENDING PACKET:", e)

        print("=== END SEND PACKET ===\n")

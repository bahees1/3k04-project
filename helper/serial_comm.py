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

    def send_packet(self, dashboard):
        """
        Send packet using dashboard.build_serial_packet().
        This version handles mode-aware, scaled bytes.
        """
        if not self.ser or not self.ser.is_open:
            print("ERROR: Serial not connected. Cannot send packet.\n")
            return

        print("\n=== SENDING PACKET ===")

        # Build packet using dashboard method
        try:
            packet = dashboard.build_serial_packet()
        except Exception as e:
            print("[ERROR] Failed to build packet:", e)
            return

        # Show packet contents for debugging
        packet_bytes = list(packet)
        print(f"[DEBUG] Packet ({len(packet_bytes)} bytes): {packet_bytes}")
        print(f"[DEBUG] Packet HEX: {[f'0x{b:02X}' for b in packet_bytes]}")

        # Send packet
        try:
            bytes_written = self.ser.write(packet)
            self.ser.flush()
            print(f"[DEBUG] Bytes written: {bytes_written}")

            # Give MCU time to respond
            time.sleep(0.05)
            if self.ser.in_waiting > 0:
                resp = self.ser.read(self.ser.in_waiting)
                print("RESPONSE RECEIVED:", list(resp))
                print("RESPONSE HEX:", [f"0x{b:02X}" for b in resp])
            else:
                print("No response received from pacemaker.")

        except Exception as e:
            print("[ERROR] Failed to send packet:", e)

        print("=== END SEND PACKET ===\n")

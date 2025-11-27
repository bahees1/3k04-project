import serial
import struct

class PacemakerSerial:
    def __init__(self, port="COM7", baud=115200):
        self.port = port
        self.baud = baud
        self.ser = None

    def connect(self):
        try:
            self.ser = serial.Serial(self.port, self.baud, timeout=1)
            print("Serial connected.")
            return True
        except Exception as e:
            print("Serial Error:", e)
            return False

    def close(self):
        if self.ser:
            self.ser.close()

    def send_packet(self, param_dict):
        """
        Send the 18-byte packet to the pacemaker with 3-byte padding at the start
        """
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
            if key.startswith("Reserved"):
                byte_val = 0
            elif key == "mode":
                byte_val = param_dict.get("mode", 0)
            elif key == "ActivityThreshold":
                byte_val = param_dict.get("ActivityThreshold", 0)
            else:
                value = param_dict.get(key, 0)
                byte_val = int(value) & 0xFF
            packet_bytes.append(byte_val)

        # Only send the first 18 bytes
        packet_bytes = packet_bytes[:18]

        
        packet = struct.pack(f"{len(packet_bytes)}B", *packet_bytes)
        if self.ser:
            self.ser.write(packet)
            print("Packet sent:", packet_bytes)
        else:
            print("Serial not connected.")


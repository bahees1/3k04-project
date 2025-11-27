# DASHBOARD MODULE
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from helper import storage, patient_helpers, param_helpers, gui_helpers
from helper.serial_comm import PacemakerSerial
import struct

entry_bg = "#f8f8f8"
entry_fg = "black"

# Order of parameters in the data packet
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
    "Activity Threshold",
    "Reaction Time",
    "Response Factor",
    "Recovery Time"
]

ACTIVITY_THRESHOLD_MAP = {
    "V-Low": 1,
    "Low": 2,
    "Med-Low": 3,
    "Med": 4,
    "Med-High": 5,
    "High": 6,
    "V-High": 7
}


class Dashboard(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Set current mode and load existing patients
        self.patient_entries = {}
        self.param_entries = {}
        self.patient = None
        self.patients = storage.load_all_patients()
        self.current_mode = tk.StringVar(value="AOO")

        # Build UI
        self.build_header()
        self.build_main_content()
        self.build_footer()

        # Load patients into dropdown
        self.refresh_patient_dropdown()
        self.update_mode_parameters()

    # -----------------------------
    # Header Section
    # -----------------------------
    def build_header(self):
        header = tk.Frame(self)
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        header.grid_columnconfigure(0, weight=1)

        # Title Label
        tk.Label(
            header, text="Pacemaker DCM Dashboard", font=("Arial", 18, "bold")
        ).grid(row=0, column=0, sticky="w")

        # Pacemaker Status Label
        self.pacemaker_status_label = tk.Label(
            header, text="Pacemaker Status: Disconnected", font=("Arial", 12), fg="red"
        )
        self.pacemaker_status_label.grid(row=0, column=1, sticky="w", pady=(5, 0))

        # Connect / Quit buttons
        button_frame = tk.Frame(header)
        button_frame.grid(row=1, column=1, sticky="e")

        connect_btn = tk.Button(button_frame, text="Connect", command=self.connect_pacemaker)
        connect_btn.pack(side="left", padx=5)

        quit_btn = tk.Button(button_frame, text="Quit", command=self.disconnect_pacemaker)
        quit_btn.pack(side="left", padx=5)

    # -----------------------------
    # Main Content Section
    # -----------------------------
    def build_main_content(self):
        main_content = tk.Frame(self)
        main_content.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        main_content.grid_columnconfigure(0, weight=1)
        main_content.grid_columnconfigure(1, weight=1)

        # patient and mode selector row
        selector_frame = tk.Frame(main_content)
        selector_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        tk.Label(selector_frame, text="Select Patient:").pack(side="left", padx=5)
        self.patient_var = tk.StringVar()
        self.patient_dropdown = tk.OptionMenu(selector_frame, self.patient_var, "")
        self.patient_dropdown.pack(side="left")

        # pacing mode dropdown 
        tk.Label(selector_frame, text="Pacing Mode:").pack(side="left", padx=(15, 5))
        self.mode_dropdown = tk.OptionMenu(selector_frame, self.current_mode, "AOO", "VOO", "AAI", "VVI", "AOOR", "VOOR", "AAIR", "VVIR")
        self.mode_dropdown.pack(side="left")
        self.current_mode.trace_add("write", lambda *args: self.update_mode_parameters()) # keeps watch of what mode is selected, calls the update param function when changes

        # button to switch to egram view
        tk.Button(
            selector_frame,
            text="Egram View",
            command=self.open_egram_view
        ).pack(side="right", padx=10)
        # Left Panel: Patient + Device Info
        patient_frame = tk.LabelFrame(main_content, text="Patient Info & Device")
        patient_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        # Patient info fields
        for i, field in enumerate(["ID", "Name"]):
            gui_helpers.create_labeled_entry(
                parent=patient_frame,
                label_text=field,
                row=i,
                entry_dict=self.patient_entries,
                read_only=(field == "ID")
            )

        # Device info
        for j, field in enumerate(["Model", "Serial"], start=2):
            gui_helpers.create_labeled_entry(
                parent=patient_frame,
                label_text=field,
                row=j,
                entry_dict=self.param_entries
            )

        # Right Panel: Device Parameters
        param_frame = tk.LabelFrame(main_content, text="Device Parameters")
        param_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)

        for i, field in enumerate(param_helpers.PARAM_FIELDS):
            if field in ["Model", "Serial"]:
                continue

            # Special dropdown for Activity Threshold
            if field == "Activity Threshold":
                self.activity_threshold_var = tk.StringVar()

                label = tk.Label(param_frame, text="Activity Threshold")
                label.grid(row=i, column=0, padx=5, pady=5)

                dropdown = tk.OptionMenu(
                    param_frame,
                    self.activity_threshold_var,
                    "V-Low", "Low", "Med-Low", "Med", "Med-High", "High", "V-High"
                )
                dropdown.grid(row=i, column=1, padx=5, pady=5)

                # Register in entries dict
                self.param_entries["Activity Threshold"] = dropdown
                continue

            # All other parameters → normal labeled entry
            gui_helpers.create_labeled_entry(
                parent=param_frame,
                label_text=field,
                row=i,
                entry_dict=self.param_entries
            )


    # -----------------------------
    # Footer Section
    # -----------------------------
    def build_footer(self):
        footer = tk.Frame(self)
        footer.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        gui_helpers.create_footer_buttons(footer, self)

    # -----------------------------
    # Visual indiciators for pacemaker connection
    # -----------------------------
    def connect_pacemaker(self):
        
        # Initializes the serial connection to the pacemaker.
        # Updates the pacemaker status label.
        
        if hasattr(self, "serial_link") and self.serial_link.ser and self.serial_link.ser.is_open:
            print("Serial already connected.")
            self.pacemaker_status_label.config(text="Pacemaker Status: Connected", fg="green")
            return

        self.serial_link = PacemakerSerial(port="COM7", baud=115200)
        success = self.serial_link.connect()
        if success:
            self.pacemaker_status_label.config(text="Pacemaker Status: Connected", fg="green")
            print("Serial connection established successfully.")
        else:
            self.pacemaker_status_label.config(text="Pacemaker Status: Disconnected", fg="red")
            print("Failed to connect to pacemaker.")
            
    def disconnect_pacemaker(self):
        if hasattr(self, "serial_link") and self.serial_link.ser:
            self.serial_link.close()
            print("Serial connection closed.")
        self.pacemaker_status_label.config(text="Pacemaker Status: Disconnected", fg="red")

    # -----------------------------
    # Patient Loading and Saving
    # -----------------------------
    def refresh_patient_dropdown(self):
        gui_helpers.refresh_patient_dropdown(self)

    def load_selected_patient(self, name):
        patient = storage.load_patient_by_name(name)
        
        # If patient found, populate fields
        if patient:
            self.patient = patient
            patient_helpers.populate_patient_fields(self.patient_entries, patient)
            self.update_mode_parameters()
            self.patient_var.set(name)

    def update_mode_parameters(self):
        mode = self.current_mode.get()
        allowed_fields = param_helpers.MODE_PARAMETER_MAP.get(mode, [])

        # Use blank device if no patient exists
        device = {"modes": {}}
        parameters = {}

        if self.patient:
            device = self.patient.get("device", {})
            modes = device.get("modes", {})
            mode_data = modes.get(mode, {})
            parameters = mode_data.get("parameters", {})

        # Fill parameter fields
        for key, field_name in param_helpers.PARAMETER_MAPPING:
            if field_name == "Activity Threshold":
                # Update OptionMenu via StringVar
                if "Activity Threshold" in allowed_fields:
                    self.activity_threshold_var.set(parameters.get(key, "Med"))
                    self.param_entries["Activity Threshold"].config(
                        state="normal", bg="white", fg="black"
                    )
                else:
                    self.activity_threshold_var.set(parameters.get(key, ""))
                    self.param_entries["Activity Threshold"].config(
                        state="disabled", bg="#b6b4b4", fg="gray"
                    )
                continue  # skip normal Entry update

            # Standard Entry fields
            entry = self.param_entries[field_name]
            entry.config(state="normal")
            entry.delete(0, "end")
            if key in parameters:
                entry.insert(0, parameters[key])

        # Fill device model/serial
        self.param_entries["Model"].config(state="normal")
        self.param_entries["Model"].delete(0, "end")
        self.param_entries["Model"].insert(0, device.get("model", ""))

        self.param_entries["Serial"].config(state="normal")
        self.param_entries["Serial"].delete(0, "end")
        self.param_entries["Serial"].insert(0, device.get("serial", ""))

        # Enable/disable fields based on mode
        for field_name, entry in self.param_entries.items():
            if field_name in ["Model", "Serial"]:
                continue

            if field_name == "Activity Threshold":
                # Already handled above
                continue

            if field_name in allowed_fields:
                entry.config(state="normal", bg="#f8f8f8", fg="black")
            else:
                entry.config(state="disabled", disabledbackground="#b6b4b4", disabledforeground="gray")
                
    def clear_fields(self):
        patient_helpers.clear_fields(self)

    def save_patient(self):
        patient_helpers.save_patient_from_dashboard(self)

    def remove_patient(self):
        patient_helpers.remove_patient(self)
        
    def open_egram_view(self):
        if not self.patient:
            messagebox.showwarning("No Patient Selected", "Please select a patient before opening the Egram screen.")
            return

        screen = self.controller.frames["EgramScreen"]
        screen.set_active_patient(self.patient)
        self.controller.show_frame("EgramScreen")
    
    def mode_to_uint8(self):
    
        # Converts selected mode string into its corresponding mode byte.
        # AOO=1, VOO=2, AAI=3, VVI=4, AOOR=5, VOOR=6, AAIR=7, VVIR=8.
        mode_map = {
            "AOO": 1,
            "VOO": 2,
            "AAI": 3,
            "VVI": 4,
            "AOOR": 5,
            "VOOR": 6,
            "AAIR": 7,
            "VVIR": 8
        }

        mode_str = self.current_mode.get()
        return mode_map.get(mode_str, 1)
    
    def build_serial_packet(self):
        print("\n====================")
        print("BUILDING SERIAL PACKET (MODE-AWARE, SCALED)")
        print("====================")

        packet_bytes = []
        mode = self.current_mode.get()
        allowed_fields = param_helpers.MODE_PARAMETER_MAP.get(mode, [])

        for key in PACKET_ORDER:
            byte_val = 0  # default

            # Reserved bytes
            if key.startswith("Reserved"):
                byte_val = 0
                print(f"Reading field: {key} -> Reserved, using 0")

            # Mode byte
            elif key == "mode":
                byte_val = self.mode_to_uint8()
                print(f"Reading field: mode -> {mode} -> byte {byte_val}")

            # Activity Threshold dropdown
            elif key == "Activity Threshold":
                at_val = self.activity_threshold_var.get()
                byte_val = ACTIVITY_THRESHOLD_MAP.get(at_val, 0)
                print(f"Reading field: Activity Threshold '{at_val}' -> byte {byte_val}")

            # Skip parameters not allowed for this mode
            elif key not in allowed_fields:
                byte_val = 0
                print(f"Reading field: {key} -> not allowed for mode {mode}, defaulting 0")

            # Allowed parameters: scale if needed
            else:
                entry = self.param_entries.get(key)
                if entry:
                    raw_val = entry.get()
                    print(f"Reading field: {key} -> raw UI value: '{raw_val}'")

                    try:
                        val = float(raw_val)

                        # Scaling rules
                        if key in ["Atrial Amplitude", "Ventricular Amplitude",
                                "Atrial Sensitivity", "Ventricular Sensitivity"]:
                            send_val = int(val * 10)
                            print(f"  -> Scaling x10: {val} -> {send_val}")
                        elif key in ["VRP", "ARP", "PVARP"]:
                            send_val = int(val / 10)
                            print(f"  -> Scaling /10: {val} -> {send_val}")
                        else:
                            send_val = int(val)
                            print(f"  -> Raw integer param: {send_val}")

                        # Clamp to 0–255
                        byte_val = max(0, min(send_val, 255))
                        print(f"  -> Final byte: {byte_val} (0x{byte_val:02X})")

                    except Exception as e:
                        print(f"  -> ERROR converting '{raw_val}': {e}, defaulting 0")
                        byte_val = 0
                else:
                    print(f"  -> Entry not found for {key}, defaulting 0")

            packet_bytes.append(byte_val)

        # Ensure packet length is exactly 18 bytes
        packet_bytes = packet_bytes[:18]

        print("\nFINAL PACKET (DECIMAL):")
        print(packet_bytes)
        print("====================\n")

        return struct.pack(f"{len(packet_bytes)}B", *packet_bytes)



    # -----------------------------
    # Clock & About Modals
    # -----------------------------
    def show_clock(self):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        messagebox.showinfo("Current Date & Time", f"Current system time:\n{now}")

    def show_about(self):
        model_number = "DCM-1000"
        software_version = "v1.0.0"
        institution = "McMaster University"

        dcm_serial = "N/A"
        if self.patient and "device" in self.patient:
            device = self.patient["device"]
            if "dcm_serial" in device:
                dcm_serial = device["dcm_serial"]

        message = (
            f"Pacemaker DCM Application\n\n"
            f"Institution: {institution}\n"
            f"Model Number: {model_number}\n"
            f"Software Version: {software_version}\n"
            f"DCM Serial Number: {dcm_serial}"
        )
        messagebox.showinfo("About", message)

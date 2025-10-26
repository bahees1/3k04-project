# DASHBOARD MODULE
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from helper import storage, patient_helpers, param_helpers, gui_helpers

entry_bg = "#f8f8f8"
entry_fg = "black"


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
        self.mode_dropdown = tk.OptionMenu(selector_frame, self.current_mode, "AOO", "VOO", "AAI", "VVI")
        self.mode_dropdown.pack(side="left")
        self.current_mode.trace_add("write", lambda *args: self.update_mode_parameters()) # keeps watch of what mode is selected, calls the update param function when changes

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

        # Pull parameter fields dynamically from param_helpers
        for i, field in enumerate(param_helpers.PARAM_FIELDS):
            if field in ["Model", "Serial"]:
                continue
            
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
        self.pacemaker_status_label.config(text="Pacemaker Status: Connected", fg="green")

    def disconnect_pacemaker(self):
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
            entry = self.param_entries[field_name]
            entry.config(state="normal")
            entry.delete(0, "end")
            if key in parameters:
                entry.insert(0, parameters[key])

        # Fill device info
        self.param_entries["Model"].delete(0, "end")
        self.param_entries["Model"].insert(0, device.get("model", ""))

        self.param_entries["Serial"].delete(0, "end")
        self.param_entries["Serial"].insert(0, device.get("serial", ""))

        # Enable/disable fields based on mode
        for field_name, entry in self.param_entries.items():
            if field_name in ["Model", "Serial"]:
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

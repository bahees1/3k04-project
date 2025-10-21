import tkinter as tk
from tkinter import messagebox
from helper import storage

entry_bg = "#f8f8f8"
entry_fg = "black"

class Dashboard(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Header
        header = tk.Frame(self)
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        header.grid_columnconfigure(0, weight=1)

        title_label = tk.Label(
            header,
            text="Pacemaker DCM Dashboard",
            font=("Arial", 18, "bold")
        )
        title_label.grid(row=0, column=0, sticky="w")

        self.pacemaker_status_label = tk.Label(
            header,
            text="Pacemaker Status: Disconnected",
            font=("Arial", 12),
            fg="red",
        )
        self.pacemaker_status_label.grid(row=0, column=1, sticky="e")

        # Main content area
        main_content = tk.Frame(self)
        main_content.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        main_content.grid_columnconfigure(0, weight=1)
        main_content.grid_columnconfigure(1, weight=1)

        # Patient selector dropdown
        selector_frame = tk.Frame(main_content)
        selector_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        tk.Label(selector_frame, text="Select Patient:").pack(side="left", padx=5)
        self.patient_var = tk.StringVar()
        self.patient_dropdown = tk.OptionMenu(selector_frame, self.patient_var, "")
        self.patient_dropdown.pack(side="left")

        # Patient info panel
        patient_frame = tk.LabelFrame(main_content, text="Patient Info")
        patient_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        self.patient_entries = {}
        fields = ["ID", "Name"]
        for i, field in enumerate(fields):
            label = tk.Label(patient_frame, text=field)
            label.grid(row=i, column=0, sticky="w", padx=5, pady=5)
            entry = tk.Entry(patient_frame, bg=entry_bg, fg=entry_fg, insertbackground="black")
            entry.grid(row=i, column=1, padx=5, pady=5)
            if field == "ID":
                entry.config(state="disabled")  # Make ID field read-only
            self.patient_entries[field] = entry

        # Device parameters panel
        param_frame = tk.LabelFrame(main_content, text="Device & Parameters")
        param_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)

        self.param_entries = {}
        param_fields = [
            "Model", "Serial",
            "Lower Rate Limit", "Upper Rate Limit",
            "Atrial Amplitude", "Ventricular Amplitude",
            "Atrial Pulse Width", "Ventricular Pulse Width"
        ]
        for i, field in enumerate(param_fields):
            label = tk.Label(param_frame, text=field)
            label.grid(row=i, column=0, sticky="w", padx=5, pady=5)
            entry = tk.Entry(param_frame, bg=entry_bg, fg=entry_fg, insertbackground="black")
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.param_entries[field] = entry

        # Footer buttons
        footer = tk.Frame(self)
        footer.grid(row=2, column=0, sticky="ew", padx=10, pady=10)

        new_button = tk.Button(footer, text="New Patient", command=self.clear_fields)
        new_button.grid(row=0, column=0, padx=5)

        save_button = tk.Button(footer, text="Save Patient", command=self.save_patient)
        save_button.grid(row=0, column=1, padx=5)

        about_button = tk.Button(footer, text="About", command=self.show_about)
        about_button.grid(row=0, column=2, padx=5)

        logout_button = tk.Button(
            footer,
            text="Logout",
            command=lambda: controller.show_frame("Login"),
            fg="black"
        )
        logout_button.grid(row=0, column=3, padx=5)

        # Load patients into memory and populate dropdown
        self.patients = storage.load_all_patients()
        self.patient = None
        self.refresh_patient_dropdown()

    # -----------------------------
    # Refresh dropdown
    # -----------------------------
    def refresh_patient_dropdown(self):
        menu = self.patient_dropdown["menu"]
        menu.delete(0, "end")

        if not self.patients:
            self.patient_var.set("No patients found")
            return

        for p in self.patients:
            name = p.get("name", "Unnamed")
            menu.add_command(label=name, command=lambda n=name: self.load_selected_patient(n))

        if self.patient:
            self.patient_var.set(self.patient.get("name", ""))
        else:
            first_name = self.patients[0].get("name", "")
            self.patient_var.set(first_name)
            self.load_selected_patient(first_name)

    # -----------------------------
    # Load selected patient
    # -----------------------------
    def load_selected_patient(self, name):
        patient = storage.load_patient_by_name(name)
        if patient:
            self.patient = patient
            self.populate_fields(patient)
            self.patient_var.set(name)

    # -----------------------------
    # Populate input fields
    # -----------------------------
    def populate_fields(self, patient):
        self.patient_entries["ID"].config(state="normal")
        self.patient_entries["ID"].delete(0, tk.END)
        self.patient_entries["ID"].insert(0, patient.get("id", ""))
        self.patient_entries["ID"].config(state="disabled")

        self.patient_entries["Name"].delete(0, tk.END)
        self.patient_entries["Name"].insert(0, patient.get("name", ""))

        device = patient.get("device", {})
        self.param_entries["Model"].delete(0, tk.END)
        self.param_entries["Model"].insert(0, device.get("model", ""))

        self.param_entries["Serial"].delete(0, tk.END)
        self.param_entries["Serial"].insert(0, device.get("serial", ""))

        parameters = device.get("parameters", {})
        mapping = [
            ("lower_rate_limit", "Lower Rate Limit"),
            ("upper_rate_limit", "Upper Rate Limit"),
            ("atrial_amplitude", "Atrial Amplitude"),
            ("ventricular_amplitude", "Ventricular Amplitude"),
            ("atrial_pulse_width", "Atrial Pulse Width"),
            ("ventricular_pulse_width", "Ventricular Pulse Width")
        ]
        for key, field_name in mapping:
            self.param_entries[field_name].delete(0, tk.END)
            self.param_entries[field_name].insert(0, parameters.get(key, ""))

    # -----------------------------
    # Clear input fields for new patient
    # -----------------------------
    def clear_fields(self):
        for key in self.patient_entries:
            if key == "ID":
                continue
            self.patient_entries[key].delete(0, tk.END)
        for key in self.param_entries:
            self.param_entries[key].delete(0, tk.END)
        self.patient = None

        # Generate and insert new ID
        new_id = self.generate_unique_patient_id()
        self.patient_entries["ID"].config(state="normal")
        self.patient_entries["ID"].delete(0, tk.END)
        self.patient_entries["ID"].insert(0, new_id)
        self.patient_entries["ID"].config(state="disabled")

        self.patient_var.set("New Patient")

    # -----------------------------
    # Generate unique patient ID
    # -----------------------------
    def generate_unique_patient_id(self):
        if not self.patients:
            return "P001"
        existing_ids = []
        for p in self.patients:
            pid = p.get("id", "")
            if pid.startswith("P") and pid[1:].isdigit():
                existing_ids.append(int(pid[1:]))
        next_num = max(existing_ids, default=0) + 1
        return f"P{next_num:03d}"

    # -----------------------------
    # Save patient info
    # -----------------------------
    def save_patient(self):
        # Retrieve and sanitize input values
        patient_id = self.patient_entries["ID"].get().strip()
        patient_name = self.patient_entries["Name"].get().strip().capitalize()
        model = self.param_entries["Model"].get().strip().capitalize()
        serial = self.param_entries["Serial"].get().strip().capitalize()

        # Validation checks
        if not patient_name:
            messagebox.showwarning("Missing Field", "Patient Name is required before saving.")
            return
        if not model:
            messagebox.showwarning("Missing Field", "Device Model is required before saving.")
            return
        if not serial:
            messagebox.showwarning("Missing Field", "Device Serial is required before saving.")
            return

        # Collect device parameters
        parameters = {}
        for key, field_name in [
            ("lower_rate_limit", "Lower Rate Limit"),
            ("upper_rate_limit", "Upper Rate Limit"),
            ("atrial_amplitude", "Atrial Amplitude"),
            ("ventricular_amplitude", "Ventricular Amplitude"),
            ("atrial_pulse_width", "Atrial Pulse Width"),
            ("ventricular_pulse_width", "Ventricular Pulse Width")
        ]:
            value = self.param_entries[field_name].get().strip()
            if value:
                parameters[key] = value

        # Construct patient data structure
        new_patient = {
            "id": patient_id,
            "name": patient_name,
            "device": {
                "model": model,
                "serial": serial,
                "parameters": parameters
            }
        }

        # Save data
        storage.save_patient(new_patient)
        self.patients = storage.load_all_patients()
        self.patient = new_patient
        self.refresh_patient_dropdown()
        self.patient_var.set(patient_name)

        messagebox.showinfo("Saved", f"Patient {patient_id} saved successfully!")

    # -----------------------------
    # About info
    # -----------------------------
    def show_about(self):
        messagebox.showinfo("About", "Pacemaker DCM v1.0\nMcMaster University")

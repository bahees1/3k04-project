import tkinter as tk
from tkinter import messagebox
from helper import storage, patient_helpers, param_helpers, gui_helpers

entry_bg = "#f8f8f8"
entry_fg = "black"

class Dashboard(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.patient_entries = {}
        self.param_entries = {}
        self.patient = None
        self.patients = storage.load_all_patients()

        # Build GUI sections
        self.build_header()
        self.build_main_content()
        self.build_footer()

        # Load patients into dropdown
        self.refresh_patient_dropdown()

    # -----------------------------
    # Header section
    # -----------------------------
    def build_header(self):
        header = tk.Frame(self)
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        header.grid_columnconfigure(0, weight=1)

        tk.Label(
            header, text="Pacemaker DCM Dashboard", font=("Arial", 18, "bold")
        ).grid(row=0, column=0, sticky="w")

        self.pacemaker_status_label = tk.Label(
            header, text="Pacemaker Status: Disconnected", font=("Arial", 12), fg="red"
        )
        self.pacemaker_status_label.grid(row=0, column=1, sticky="e")

    # -----------------------------
    # Main content section
    # -----------------------------
    def build_main_content(self):
        main_content = tk.Frame(self)
        main_content.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        main_content.grid_columnconfigure(0, weight=1)
        main_content.grid_columnconfigure(1, weight=1)

        # Patient selector
        selector_frame = tk.Frame(main_content)
        selector_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        tk.Label(selector_frame, text="Select Patient:").pack(side="left", padx=5)
        self.patient_var = tk.StringVar()
        self.patient_dropdown = tk.OptionMenu(selector_frame, self.patient_var, "")
        self.patient_dropdown.pack(side="left")

        # Left panel: Patient Info
        patient_frame = tk.LabelFrame(main_content, text="Patient Info")
        patient_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        for i, field in enumerate(["ID", "Name"]):
            gui_helpers.create_labeled_entry(
                parent=patient_frame,
                label_text=field,
                row=i,
                entry_dict=self.patient_entries,
                read_only=(field=="ID")
            )

        # Right panel: Device & Parameters
        param_frame = tk.LabelFrame(main_content, text="Device & Parameters")
        param_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)

        for i, field in enumerate(param_helpers.PARAM_FIELDS):
            gui_helpers.create_labeled_entry(
                parent=param_frame,
                label_text=field,
                row=i,
                entry_dict=self.param_entries
            )

    # -----------------------------
    # Footer section
    # -----------------------------
    def build_footer(self):
        footer = tk.Frame(self)
        footer.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        gui_helpers.create_footer_buttons(footer, self)

    # -----------------------------
    # Refresh patient dropdown
    # -----------------------------
    def refresh_patient_dropdown(self):
        gui_helpers.refresh_patient_dropdown(self)

    # -----------------------------
    # Load selected patient
    # -----------------------------
    def load_selected_patient(self, name):
        patient = storage.load_patient_by_name(name)
        if patient:
            self.patient = patient
            patient_helpers.populate_patient_fields(self.patient_entries, patient)
            param_helpers.populate_parameter_entries(self.param_entries, patient.get("device", {}))
            self.patient_var.set(name)

    # -----------------------------
    # Clear all fields
    # -----------------------------
    def clear_fields(self):
        patient_helpers.clear_fields(self)

    # -----------------------------
    # Save patient
    # -----------------------------
    def save_patient(self):
        patient_helpers.save_patient(self)

    # -----------------------------
    # Remove patient
    # -----------------------------
    def remove_patient(self):
        patient_helpers.remove_patient(self)

    # -----------------------------
    # About info
    # -----------------------------
    def show_about(self):
        messagebox.showinfo("About", "Pacemaker DCM v1.0\nMcMaster University")

import tkinter as tk
from tkinter import messagebox
import json
import os

entry_bg = "#f8f8f8"
entry_fg = "black"

class Dashboard(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # ----------------------------
        # Configure frame expansion
        # ----------------------------
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # ========================
        # Header
        # ========================
        header = tk.Frame(self)
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        header.grid_columnconfigure(0, weight=1)
        header.grid_columnconfigure(1, weight=0)

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

        # ========================
        # Main content (two panels)
        # ========================
        main_content = tk.Frame(self)
        main_content.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        main_content.grid_columnconfigure(0, weight=1)
        main_content.grid_columnconfigure(1, weight=1)

        # -------- Left Panel: Patient Info --------
        patient_frame = tk.LabelFrame(main_content, text="Patient Info")
        patient_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        self.patient_entries = {}
        for i, field in enumerate(["ID", "Name"]):
            label = tk.Label(patient_frame, text=field)
            label.grid(row=i, column=0, sticky="w", padx=5, pady=5)
            entry = tk.Entry(patient_frame, bg=entry_bg, fg=entry_fg)
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.patient_entries[field] = entry

        # -------- Right Panel: Device & Parameters --------
        param_frame = tk.LabelFrame(main_content, text="Device & Parameters")
        param_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
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
            entry = tk.Entry(param_frame, bg=entry_bg, fg=entry_fg)
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.param_entries[field] = entry

        
# main dashboard frame goes here screen after login
import tkinter as tk
from tkinter import messagebox


class Dashboard(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Allow the frame to expand fully
        self.grid_rowconfigure(1, weight=1)  # main content expands
        self.grid_columnconfigure(0, weight=1)

        # ===========================
        # Header Section
        # ===========================
        header = tk.Frame(self)
        header.grid(row=0, column=0, sticky="ew", pady=(10, 5))

        tk.Label(
            header,
            text="Pacemaker DCM Dashboard",
            font=("Arial", 18, "bold"),
        ).pack()

        


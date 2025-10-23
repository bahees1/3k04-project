import tkinter as tk
from tkinter import messagebox
from helper import storage, param_helpers

def generate_unique_patient_id(dashboard):
    patients = dashboard.patients
    if not patients:
        return "P001"
    existing_ids = [int(p["id"][1:]) for p in patients if p.get("id","").startswith("P") and p["id"][1:].isdigit()]
    next_num = max(existing_ids, default=0) + 1
    return f"P{next_num:03d}"

def populate_patient_fields(entries, patient):
    entries["ID"].config(state="normal")
    entries["ID"].delete(0, tk.END)
    entries["ID"].insert(0, patient.get("id", ""))
    entries["ID"].config(state="disabled")
    entries["Name"].delete(0, tk.END)
    entries["Name"].insert(0, patient.get("name", ""))

def clear_fields(dashboard):
    for key in dashboard.patient_entries:
        if key == "ID":
            continue
        dashboard.patient_entries[key].delete(0, "end")
    for key in dashboard.param_entries:
        dashboard.param_entries[key].delete(0, "end")
    dashboard.patient = None
    # Generate new ID
    new_id = generate_unique_patient_id(dashboard)
    dashboard.patient_entries["ID"].config(state="normal")
    dashboard.patient_entries["ID"].delete(0, "end")
    dashboard.patient_entries["ID"].insert(0, new_id)
    dashboard.patient_entries["ID"].config(state="disabled")
    dashboard.patient_var.set("New Patient")

def save_patient(dashboard):
    patient_id = dashboard.patient_entries["ID"].get().strip()
    patient_name = dashboard.patient_entries["Name"].get().strip().capitalize()
    model = dashboard.param_entries["Model"].get().strip().capitalize()
    serial = dashboard.param_entries["Serial"].get().strip().capitalize()

    if not patient_name or not model or not serial:
        messagebox.showwarning("Missing Fields", "Patient Name, Model, and Serial are required.")
        return

    parameters = {}
    for key, field_name in param_helpers.PARAMETER_MAPPING:
        value = dashboard.param_entries[field_name].get().strip()
        if value:
            parameters[key] = value

    new_patient = {
        "id": patient_id,
        "name": patient_name,
        "device": {"model": model, "serial": serial, "parameters": parameters}
    }

    storage.save_patient(new_patient)
    dashboard.patients = storage.load_all_patients()
    dashboard.patient = new_patient
    dashboard.refresh_patient_dropdown()
    dashboard.patient_var.set(patient_name)
    messagebox.showinfo("Saved", f"Patient {patient_id} saved successfully!")

def remove_patient(dashboard):
    if not dashboard.patient:
        messagebox.showwarning("No Selection", "No patient selected to remove.")
        return

    patient_id = dashboard.patient.get("id")
    confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to remove patient {patient_id}?")
    if confirm:
        storage.delete_patient(patient_id)
        dashboard.patients = storage.load_all_patients()
        dashboard.patient = None
        dashboard.clear_fields()
        dashboard.refresh_patient_dropdown()

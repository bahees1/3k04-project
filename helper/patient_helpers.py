import tkinter as tk
from tkinter import messagebox
from helper import storage, param_helpers

# function used to generate a unique patient ID
def generate_unique_patient_id(dashboard):
    patients = dashboard.patients
    
    # If no patients exist, start with P001
    if not patients:
        return "P001"
    
    existing_ids = []
    for patient in patients:
        patient_id = patient.get("id", "")
        # Check if the ID starts with "P" and the rest is a number
        if patient_id.startswith("P") and patient_id[1:].isdigit():
            existing_ids.append(int(patient_id[1:]))
    
    # Determine the next number
    next_num = max(existing_ids, default=0) + 1
    
    # Return the formatted new ID
    return f"P{next_num:03d}"


# Populate patient fields in the dashboard
def populate_patient_fields(entries, patient):
    entries["ID"].config(state="normal")
    entries["ID"].delete(0, tk.END)
    entries["ID"].insert(0, patient.get("id", ""))
    entries["ID"].config(state="disabled")
    entries["Name"].delete(0, tk.END)
    entries["Name"].insert(0, patient.get("name", ""))


# Clear all fields for a new patient
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
    
    # Set new ID in the ID entry
    dashboard.patient_entries["ID"].config(state="normal")
    dashboard.patient_entries["ID"].delete(0, "end")
    dashboard.patient_entries["ID"].insert(0, new_id)
    dashboard.patient_entries["ID"].config(state="disabled")
    dashboard.patient_var.set("New Patient")
    
    dashboard.update_mode_parameters()


# -----------------------------
# Validation helper for parameter ranges
# -----------------------------
def validate_parameters(params):
    errors = []

    # Helper to check if value is in range
    def in_range(val, low, high):
        try:
            num = float(val)
            return low <= num <= high
        except ValueError:
            return False

    # Lower/Upper Rate Limit
    if not in_range(params.get("lower_rate_limit", 0), 30, 175):
        errors.append("Lower Rate Limit must be between 30 and 175 ppm.")
        
    if not in_range(params.get("upper_rate_limit", 0), 50, 175):
        errors.append("Upper Rate Limit must be between 50 and 175 ppm.")
    else:
        try:
            if float(params["upper_rate_limit"]) <= float(params["lower_rate_limit"]):
                errors.append("Upper Rate Limit must be higher than Lower Rate Limit.")
        except:
            pass

    # Common parameter ranges
    for key, label, low, high, unit in [
        ("atrial_amplitude", "Atrial Amplitude", 0.5, 7.0, "V"),
        ("ventricular_amplitude", "Ventricular Amplitude", 0.5, 7.0, "V"),
        ("atrial_pulse_width", "Atrial Pulse Width", 0.05, 1.9, "ms"),
        ("ventricular_pulse_width", "Ventricular Pulse Width", 0.05, 1.9, "ms"),
        ("atrial_sensitivity", "Atrial Sensitivity", 0.25, 10.0, "mV"),
        ("ventricular_sensitivity", "Ventricular Sensitivity", 0.25, 10.0, "mV"),
        ("arp", "ARP", 150, 500, "ms"),
        ("vrp", "VRP", 150, 500, "ms"),
        ("pvarp", "PVARP", 150, 500, "ms"),
    ]:
        # Check to see if value fits within range
        val = params.get(key)
        if val and not in_range(val, low, high):
            errors.append(f"{label} must be between {low} and {high} {unit}.")

    # Rate Smoothing
    smoothing_allowed = {"0", "3", "6", "9", "12", "15", "18", "21", "25"}
    
    if params.get("rate_smoothing") and params.get("rate_smoothing") not in smoothing_allowed:
        errors.append("Rate Smoothing must be one of: 0, 3, 6, 9, 12, 15, 18, 21, 25.")

    # Hysteresis
    hysteresis_val = params.get("hysteresis", "")
    if hysteresis_val and hysteresis_val.lower() != "off":
        try:
            lrl = float(params.get("lower_rate_limit", 0))
            hys_val = float(hysteresis_val)
            if abs(hys_val - lrl) > 0.1:
                errors.append("Hysteresis must be 'Off' or equal to the Lower Rate Limit.")
        except ValueError:
            errors.append("Hysteresis must be 'Off' or a numeric value equal to LRL.")

    # Show error popup if invalid
    if errors:
        messagebox.showerror("Invalid Parameters", "\n".join(errors))
        return False
    return True


# Save patient data from dashboard
def save_patient_from_dashboard(dashboard):
    patient_id = dashboard.patient_entries["ID"].get().strip()
    patient_name = dashboard.patient_entries["Name"].get().strip().capitalize()
    model = dashboard.param_entries["Model"].get().strip().capitalize()
    serial = dashboard.param_entries["Serial"].get().strip().capitalize()
    mode = dashboard.current_mode.get()

    # User should input atleast patient name, device model and serial before saving
    if not patient_name or not model or not serial:
        messagebox.showwarning("Missing Fields", "Patient Name, Model, and Serial are required.")
        return

    existing_patients = storage.load_all_patients()
    existing_dcm_serials = []
    
    # Gather existing DCM serials to ensure uniqueness
    for p in existing_patients:
        if "device" in p and "dcm_serial" in p["device"]:
            existing_dcm_serials.append(p["device"]["dcm_serial"])

    # Generate unique DCM serial if new patient
    if dashboard.patient and "device" in dashboard.patient and "dcm_serial" in dashboard.patient["device"]:
        dcm_serial = dashboard.patient["device"]["dcm_serial"]
    else:
        next_num = len(existing_dcm_serials) + 1
        dcm_serial = "DCM-" + str(next_num).zfill(3)

    # Gather parameters from entries
    parameters = {}
    for key, field_name in param_helpers.PARAMETER_MAPPING:
        value = dashboard.param_entries[field_name].get().strip()
        if value:
            parameters[key] = value

    # -----------------------------
    # Validate parameters before saving
    # -----------------------------
    if not validate_parameters(parameters):
        return

    # Build modes dictionary
    modes = {}
    if dashboard.patient and "device" in dashboard.patient:
        modes = dashboard.patient["device"].get("modes", {})

    modes[mode] = {"parameters": parameters}

    new_patient = {
        "id": patient_id,
        "name": patient_name,
        "device": {
            "model": model,
            "serial": serial,
            "dcm_serial": dcm_serial,
            "modes": modes
        }
    }

    # Save patient data to storage
    storage.save_patient_to_file(new_patient)
    dashboard.patients = storage.load_all_patients()
    dashboard.patient = new_patient
    dashboard.refresh_patient_dropdown()
    dashboard.patient_var.set(patient_name)
    messagebox.showinfo("Saved", f"Patient {patient_id} saved successfully!")


def remove_patient(dashboard):
    # Remove the currently loaded patient
    if not dashboard.patient:
        messagebox.showwarning("No Selection", "No patient selected to remove.")
        return

    # Get patient ID and confirm deletion
    patient_id = dashboard.patient.get("id")
    confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to remove patient {patient_id}?")
    if confirm:
        storage.delete_patient(patient_id)
        dashboard.patients = storage.load_all_patients()
        dashboard.patient = None
        dashboard.clear_fields()
        dashboard.refresh_patient_dropdown()

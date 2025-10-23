# place to hold and manage pacing parameters (LRL, URL, etc...)
PARAM_FIELDS = [
    "Model", "Serial",
    "Lower Rate Limit", "Upper Rate Limit",
    "Atrial Amplitude", "Ventricular Amplitude",
    "Atrial Pulse Width", "Ventricular Pulse Width"
]

PARAMETER_MAPPING = [
    ("lower_rate_limit", "Lower Rate Limit"),
    ("upper_rate_limit", "Upper Rate Limit"),
    ("atrial_amplitude", "Atrial Amplitude"),
    ("ventricular_amplitude", "Ventricular Amplitude"),
    ("atrial_pulse_width", "Atrial Pulse Width"),
    ("ventricular_pulse_width", "Ventricular Pulse Width")
]

def populate_parameter_entries(entries, device):
    parameters = device.get("parameters", {})
    entries["Model"].delete(0, "end")
    entries["Model"].insert(0, device.get("model", ""))
    entries["Serial"].delete(0, "end")
    entries["Serial"].insert(0, device.get("serial", ""))
    for key, field_name in PARAMETER_MAPPING:
        entries[field_name].delete(0, "end")
        entries[field_name].insert(0, parameters.get(key, ""))

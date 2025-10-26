# PARAM HELPERS

# place to define parameter fields and mappings
PARAM_FIELDS = [
    "Model", "Serial",
    "Lower Rate Limit", "Upper Rate Limit",
    "Atrial Amplitude", "Ventricular Amplitude",
    "Atrial Pulse Width", "Ventricular Pulse Width",
    "ARP", "VRP",
    "Atrial Sensitivity", "Ventricular Sensitivity",
    "PVARP", "Hysteresis",
    "Rate Smoothing"
]

# Mapping between internal parameter keys and UI field names
PARAMETER_MAPPING = [
    ("lower_rate_limit", "Lower Rate Limit"),
    ("upper_rate_limit", "Upper Rate Limit"),
    ("atrial_amplitude", "Atrial Amplitude"),
    ("ventricular_amplitude", "Ventricular Amplitude"),
    ("atrial_pulse_width", "Atrial Pulse Width"),
    ("ventricular_pulse_width", "Ventricular Pulse Width"),
    ("arp", "ARP"),
    ("vrp", "VRP"),
    ("atrial_sensitivity", "Atrial Sensitivity"),
    ("ventricular_sensitivity", "Ventricular Sensitivity"),
    ("pvarp", "PVARP"),
    ("hysteresis", "Hysteresis"),
    ("rate_smoothing", "Rate Smoothing")
]

# Define which parameters are editable for each pacing mode
MODE_PARAMETER_MAP = {
    "AOO": [
        "Lower Rate Limit",
        "Upper Rate Limit",
        "Atrial Amplitude",
        "Atrial Pulse Width"
    ],
    "VOO": [
        "Lower Rate Limit",
        "Upper Rate Limit",
        "Ventricular Amplitude",
        "Ventricular Pulse Width"
    ],
    "AAI": [
        "Lower Rate Limit",
        "Upper Rate Limit",
        "Atrial Amplitude",
        "Atrial Pulse Width",
        "Atrial Sensitivity",
        "ARP",
        "PVARP",
        "Hysteresis",
        "Rate Smoothing"
    ],
    "VVI": [
        "Lower Rate Limit",
        "Upper Rate Limit",
        "Ventricular Amplitude",
        "Ventricular Pulse Width",
        "Ventricular Sensitivity",
        "VRP",
        "Hysteresis",
        "Rate Smoothing"
    ]
}



def populate_parameter_entries(entries, device):
    #Populate the device and parameter fields in the UI from the patient/device data
    parameters = device.get("parameters", {})

    # Device-level fields
    entries["Model"].delete(0, "end")
    entries["Model"].insert(0, device.get("model", ""))

    entries["Serial"].delete(0, "end")
    entries["Serial"].insert(0, device.get("serial", ""))

    # Parameter fields
    for key, field_name in PARAMETER_MAPPING:
        entries[field_name].delete(0, "end")
        entries[field_name].insert(0, parameters.get(key, ""))

import pytest
import tkinter as tk
from unittest import mock
from gui.dashboard import Dashboard

# -----------------------------
# Fixtures
# -----------------------------
@pytest.fixture
def mock_controller():
    ctrl = mock.MagicMock()
    ctrl.data = {"patients": []}
    ctrl.data_path = "mock_path.json"
    return ctrl

@pytest.fixture
def dashboard(mock_controller):
    # Create a real hidden Tk root
    root = tk.Tk()
    root.withdraw()  # hide the GUI
    dash = Dashboard(root, mock_controller)
    yield dash
    root.destroy()  # clean up after tests

# -----------------------------
# Pacemaker connection tests
# -----------------------------
def test_connect_disconnect(dashboard):
    dashboard.connect_pacemaker()
    assert dashboard.pacemaker_status_label.cget("text") == "Pacemaker Status: Connected"
    assert dashboard.pacemaker_status_label.cget("fg") == "green"

    dashboard.disconnect_pacemaker()
    assert dashboard.pacemaker_status_label.cget("text") == "Pacemaker Status: Disconnected"
    assert dashboard.pacemaker_status_label.cget("fg") == "red"

# -----------------------------
# Patient loading test
# -----------------------------
def test_load_selected_patient(dashboard):
    patient_data = {"name": "John", "device": {"model": "X", "serial": "123"}}

    with mock.patch("helper.storage.load_patient_by_name", return_value=patient_data):
        with mock.patch("helper.patient_helpers.populate_patient_fields") as pop_mock:
            dashboard.load_selected_patient("John")
            pop_mock.assert_called_once_with(dashboard.patient_entries, patient_data)
            assert dashboard.patient == patient_data
            assert dashboard.patient_var.get() == "John"

# -----------------------------
# Mode parameter update test
# -----------------------------
def test_update_mode_parameters(dashboard):
    # Mock patient with device parameters
    dashboard.patient = {
        "device": {
            "model": "X100",
            "serial": "1234",
            "modes": {
                "AOO": {"parameters": {"lower_rate": 60, "upper_rate": 120}}
            }
        }
    }

    dashboard.current_mode.set("AOO")
    dashboard.update_mode_parameters()

    # Check that device fields are populated
    assert dashboard.param_entries["Model"].get() == "X100"
    assert dashboard.param_entries["Serial"].get() == "1234"

    # Check parameter fields are filled correctly
    for key, field_name in [("lower_rate", "Lower Rate"), ("upper_rate", "Upper Rate")]:
        if field_name in dashboard.param_entries:
            assert dashboard.param_entries[field_name].get() == str(dashboard.patient["device"]["modes"]["AOO"]["parameters"][key])

# -----------------------------
# Clear, Save, Remove patient tests
# -----------------------------
def test_clear_fields(dashboard):
    with mock.patch("helper.patient_helpers.clear_fields") as clear_mock:
        dashboard.clear_fields()
        clear_mock.assert_called_once_with(dashboard)

def test_save_patient(dashboard):
    with mock.patch("helper.patient_helpers.save_patient_from_dashboard") as save_mock:
        dashboard.save_patient()
        save_mock.assert_called_once_with(dashboard)

def test_remove_patient(dashboard):
    with mock.patch("helper.patient_helpers.remove_patient") as remove_mock:
        dashboard.remove_patient()
        remove_mock.assert_called_once_with(dashboard)

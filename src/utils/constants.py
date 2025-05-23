"""Configuration constants for the ECG application."""

# BLE Configuration
TARGET_ADDRESS = "6614D41F-1CB3-77FA-3E35-C5A446EA4E3F"
CHANNEL_UUIDS = {
    1: "00008171-0000-1000-8000-00805f9b34fb",
    2: "00008172-0000-1000-8000-00805f9b34fb",
    3: "00008173-0000-1000-8000-00805f9b34fb",
    4: "00008174-0000-1000-8000-00805f9b34fb",
    5: "00008175-0000-1000-8000-00805f9b34fb",
    6: "00008176-0000-1000-8000-00805f9b34fb",
    7: "00008177-0000-1000-8000-00805f9b34fb",
    8: "00008178-0000-1000-8000-00805f9b34fb",
}

# ECG Configuration
SAMPLING_RATE = 250
SAMPLES_PER_BUFFER = 28
PLOT_UPDATE_INTERVAL = 112  # milliseconds
PLOT_BUFFER_SIZE = 375

# WebSocket Configuration
WEBSOCKET_URL = "wss://hrzmed.org"
WEBSOCKET_BUFFER_SIZE = 250

# Signal Processing
BASELINE_WANDER_ALPHA = 0.995
LOWPASS_CUTOFF_FREQUENCY = 40
FILTER_ORDER = 4

# Plot Configuration
PLOT_LIMITS = {
    'x': (0, 375),
    'y': (-16000, 16000)
}

# File Paths
LOGO_CUT_PATH = "assets/logocut.png"
LOGO_REPORT_PATH = "assets/logoreport.png"
DATA_RECORD_DIR = "data_records"
REPORTS_DIR = "reports"

# ECG Leads
ECG_LEADS = ["I", "aVR", "II", "aVF", "III", "aVL", "V1", "V4", "V2", "V5", "V3", "V6"]

# Report Configuration
REPORT_SAMPLES_COUNT = 750
GRID_COLORS = {
    'major': 'lightgray',
    'minor': 'lightgray'
}
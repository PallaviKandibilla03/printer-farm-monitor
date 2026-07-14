# ==========================================
# 3D Printer Farm Configuration
# ==========================================

# Number of printers to simulate
NUM_PRINTERS = 6

# Time between sensor updates (seconds)
UPDATE_INTERVAL = 1

# -------------------------------
# Sensor Normal Operating Ranges
# -------------------------------

NOZZLE_TEMP = (205, 215)       # °C
BED_TEMP = (58, 62)            # °C
VIBRATION = (0.15, 0.40)       # g
FLOW_RATE = (0.95, 1.05)       # Relative flow

# Printer statuses
STATUS_PRINTING = "printing"
STATUS_IDLE = "idle"
STATUS_PAUSED = "paused"

# Failure modes
FAILURE_HEALTHY = "healthy"
FAILURE_CLOG = "clog"
FAILURE_RUNOUT = "runout"
FAILURE_LAYER_SHIFT = "layer_shift"
FAILURE_BED_DRIFT = "bed_drift"

FAILURE_MODES = [
    FAILURE_HEALTHY,
    FAILURE_CLOG,
    FAILURE_RUNOUT,
    FAILURE_LAYER_SHIFT,
    FAILURE_BED_DRIFT
]
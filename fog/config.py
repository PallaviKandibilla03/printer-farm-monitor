"""
Application configuration.

Keeping all thresholds here makes the detector
easy to tune without changing business logic.
"""

# -------------------------
# Detection Thresholds
# -------------------------

NOZZLE_TEMP_THRESHOLD = 200.0

FLOW_STOP_THRESHOLD = 0.05

BED_TEMP_MIN = 50.0

VIBRATION_LAYER_SHIFT = 1.5

# -------------------------
# Aggregation
# -------------------------

AGGREGATION_INTERVAL = 60   # seconds

# -------------------------
# Logging
# -------------------------

LOG_LEVEL = "INFO"
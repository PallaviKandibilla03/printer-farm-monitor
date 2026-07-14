import random
from datetime import datetime

from config import (
    NOZZLE_TEMP,
    BED_TEMP,
    VIBRATION,
    FLOW_RATE,
    STATUS_PRINTING,
    FAILURE_HEALTHY,
    FAILURE_CLOG,
    FAILURE_RUNOUT,
    FAILURE_LAYER_SHIFT,
    FAILURE_BED_DRIFT,
)


class Printer:

    def __init__(self, printer_id):
        self.printer_id = printer_id
        self.status = STATUS_PRINTING
        self.progress = 0
        self.failure_mode = FAILURE_HEALTHY

    def generate_sensor_data(self):
        """
        Generate one set of sensor readings.
        """

        nozzle_temp = random.uniform(*NOZZLE_TEMP)
        bed_temp = random.uniform(*BED_TEMP)
        vibration = random.uniform(*VIBRATION)
        flow = random.uniform(*FLOW_RATE)

        # Update print progress
        self.progress = min(self.progress + random.randint(1, 3), 100)

        # Apply failures
        if self.failure_mode == FAILURE_CLOG:
            flow = 0.0

        elif self.failure_mode == FAILURE_RUNOUT:
            flow = 0.0

        elif self.failure_mode == FAILURE_LAYER_SHIFT:
            vibration = random.uniform(1.5, 3.0)

        elif self.failure_mode == FAILURE_BED_DRIFT:
            bed_temp = random.uniform(35, 48)

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "printer_id": self.printer_id,
            "status": self.status,
            "progress": self.progress,
            "failure_mode": self.failure_mode,
            "nozzle_temp": round(nozzle_temp, 2),
            "bed_temp": round(bed_temp, 2),
            "vibration": round(vibration, 2),
            "flow": round(flow, 2),
        }
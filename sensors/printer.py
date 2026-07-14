import random
from datetime import datetime


class Printer:
    """
    Simulates a single 3D printer with persistent failures.
    """

    FAILURE_PROBABILITY = 0.02

    FAILURE_DURATION_RANGE = (15, 30)

    COOLDOWN_RANGE = (20, 40)

    FAILURE_TYPES = [
        "nozzle_clog",
        "layer_shift",
        "bed_drift",
        "filament_runout",
    ]

    def __init__(self, printer_id):

        self.printer_id = printer_id

        self.status = "printing"

        self.progress = 0

        self.current_failure = None

        self.failure_timer = 0

        self.cooldown_timer = 0

    # ----------------------------------------------------

    def update_progress(self):

        if self.status == "printing":

            self.progress += random.randint(1, 3)

            if self.progress >= 100:

                self.progress = 0

    # ----------------------------------------------------

    def update_failure_state(self):

        # --------------------------
        # Printer recovering
        # --------------------------

        if self.cooldown_timer > 0:

            self.cooldown_timer -= 1

            return

        # --------------------------
        # Printer currently failed
        # --------------------------

        if self.current_failure is not None:

            self.failure_timer -= 1

            if self.failure_timer <= 0:

                self.current_failure = None

                self.cooldown_timer = random.randint(
                    *self.COOLDOWN_RANGE
                )

            return

        # --------------------------
        # Healthy printer
        # --------------------------

        if random.random() < self.FAILURE_PROBABILITY:

            self.current_failure = random.choice(
                self.FAILURE_TYPES
            )

            self.failure_timer = random.randint(
                *self.FAILURE_DURATION_RANGE
            )

    # ----------------------------------------------------

    def generate_sensor_data(self):

        self.update_progress()

        self.update_failure_state()

        nozzle_temp = round(random.uniform(205, 215), 2)

        bed_temp = round(random.uniform(58, 62), 2)

        vibration = round(random.uniform(0.15, 0.40), 2)

        flow = round(random.uniform(0.95, 1.05), 2)

        failure_mode = "healthy"

        # --------------------------------

        if self.current_failure == "nozzle_clog":

            failure_mode = "nozzle_clog"

            nozzle_temp = round(
                random.uniform(210, 215),
                2,
            )

            flow = 0.0

        elif self.current_failure == "filament_runout":

            failure_mode = "filament_runout"

            flow = 0.0

        elif self.current_failure == "layer_shift":

            failure_mode = "layer_shift"

            vibration = round(
                random.uniform(1.8, 2.8),
                2,
            )

        elif self.current_failure == "bed_drift":

            failure_mode = "bed_drift"

            bed_temp = round(
                random.uniform(35, 45),
                2,
            )

        return {

            "timestamp": datetime.now().isoformat(),

            "printer_id": self.printer_id,

            "status": self.status,

            "progress": self.progress,

            "failure_mode": failure_mode,

            "nozzle_temp": nozzle_temp,

            "bed_temp": bed_temp,

            "vibration": vibration,

            "flow": flow,
        }
"""
State Manager

Stores the latest sensor reading
for every printer.
"""

from models import SensorReading


class StateManager:

    def __init__(self):
        self.latest_readings: dict[str, SensorReading] = {}

    def update_reading(
        self,
        printer_id: str,
        reading: SensorReading
    ):

        self.latest_readings[printer_id] = reading

    def get_latest(self):

        return self.latest_readings
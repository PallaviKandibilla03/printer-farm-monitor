"""
Aggregation Service

Collects healthy readings
before forwarding them
to the cloud.
"""

from time import time

from config import AGGREGATION_INTERVAL

from models import (
    SensorReading,
    AlertEvent,
)

from logger import logger


class Aggregator:

    def __init__(self):

        self.buffer = []

        self.last_flush = time()

    def add(

        self,

        reading: SensorReading,

        alert: AlertEvent | None,

    ):

        # Failures are sent immediately.

        if alert:

            return None

        self.buffer.append(reading)

        elapsed = time() - self.last_flush

        if elapsed >= AGGREGATION_INTERVAL:

            summary = {

                "timestamp": reading.timestamp,

                "reading_count": len(self.buffer),

                "printers": [

                    r.printer_id

                    for r in self.buffer

                ],

            }

            self.buffer.clear()

            self.last_flush = time()

            logger.info(

                "Healthy batch ready."

            )

            return summary

        return None
from datetime import datetime
from typing import Dict

from pydantic import BaseModel

from constants import (
    EventType,
    Severity,
    EventSource,
)


class SensorReading(BaseModel):
    timestamp: datetime

    printer_id: str

    status: str

    progress: int

    nozzle_temp: float

    bed_temp: float

    vibration: float

    flow: float


class AlertEvent(BaseModel):

    # Event metadata
    event_id: str

    timestamp: datetime

    source: EventSource

    version: str

    processed: bool = False

    # Printer
    printer_id: str

    # Alert
    type: EventType

    severity: Severity

    message: str

    # Sensor snapshot
    sensor_snapshot: Dict[str, float]
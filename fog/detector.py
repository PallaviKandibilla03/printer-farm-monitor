"""
Failure Detection Engine

Contains all edge intelligence.

Input:
    SensorReading

Output:
    AlertEvent | None
"""
from datetime import datetime
import uuid

from models import (
    SensorReading,
    AlertEvent,
)

from constants import (
    EventType,
    Severity,
    EventSource,
)

from config import (
    NOZZLE_TEMP_THRESHOLD,
    FLOW_STOP_THRESHOLD,
    BED_TEMP_MIN,
    VIBRATION_LAYER_SHIFT,
)


class DetectionEngine:

    """
    Detect printer failures.

    Pure business logic.

    No FastAPI.
    No AWS.
    No logging.
    """

    @staticmethod
    def build_alert(
        reading: SensorReading,
        event_type: EventType,
        severity: Severity,
        message: str,
    ) -> AlertEvent:

        return AlertEvent(

            event_id=str(uuid.uuid4()),

            timestamp=datetime.utcnow(),

            source=EventSource.FOG_NODE,

            version="1.0",

            processed=False,

            printer_id=reading.printer_id,

            type=event_type,

            severity=severity,

            message=message,

            sensor_snapshot={

                "nozzle_temp": reading.nozzle_temp,

                "bed_temp": reading.bed_temp,

                "vibration": reading.vibration,

                "flow": reading.flow,
            },
        )

    @staticmethod
    def detect(reading: SensorReading):

        # -------------------------
        # Nozzle Clog
        # -------------------------

        if (
            reading.nozzle_temp > NOZZLE_TEMP_THRESHOLD
            and reading.flow <= FLOW_STOP_THRESHOLD
        ):

            return DetectionEngine.build_alert(

                reading,

                EventType.NOZZLE_CLOG,

                Severity.HIGH,

                "Nozzle hot while filament flow has stopped.",
            )

        # -------------------------
        # Filament Runout
        # -------------------------

        if reading.flow <= FLOW_STOP_THRESHOLD:

            return DetectionEngine.build_alert(

                reading,

                EventType.FILAMENT_RUNOUT,

                Severity.HIGH,

                "Filament flow stopped.",
            )

        # -------------------------
        # Layer Shift
        # -------------------------

        if reading.vibration >= VIBRATION_LAYER_SHIFT:

            return DetectionEngine.build_alert(

                reading,

                EventType.LAYER_SHIFT,

                Severity.MEDIUM,

                "High vibration detected.",
            )

        # -------------------------
        # Bed Drift
        # -------------------------

        if reading.bed_temp < BED_TEMP_MIN:

            return DetectionEngine.build_alert(

                reading,

                EventType.BED_TEMPERATURE_DRIFT,

                Severity.MEDIUM,

                "Bed temperature below safe threshold.",
            )

        return None
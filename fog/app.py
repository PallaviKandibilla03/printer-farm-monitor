from fastapi import FastAPI

from models import SensorReading
from detector import DetectionEngine
from state_manager import StateManager
from alert_manager import AlertManager
from aggregator import Aggregator
from cloud_sender import CloudSender
from logger import logger

app = FastAPI(
    title="3D Printer Fog Node",
    version="1.0"
)

# ----------------------------------------------------
# Services
# ----------------------------------------------------

state_manager = StateManager()
alert_manager = AlertManager()
aggregator = Aggregator()
cloud_sender = CloudSender()

@app.post("/sensor-data")
def receive_sensor_data(reading: SensorReading):
    """
    Main processing pipeline for incoming sensor data.
    """

    logger.info(
        f"Received reading from {reading.printer_id}"
    )

    # ------------------------------------------------
    # Update latest printer state
    # ------------------------------------------------

    state_manager.update_reading(
        reading.printer_id,
        reading
    )

    # ------------------------------------------------
    # Detect failures
    # ------------------------------------------------

    alert = DetectionEngine.detect(reading)

    # ------------------------------------------------
    # Process alert lifecycle
    # ------------------------------------------------

    event_type, event = alert_manager.process(
        reading.printer_id,
        alert
    )

    # ------------------------------------------------
    # Aggregate healthy readings
    # ------------------------------------------------

    summary = aggregator.add(
        reading,
        alert
    )

    # ------------------------------------------------
    # Send events to cloud
    # ------------------------------------------------

    if event_type == "NEW_ALERT":

        logger.info(
            f"Sending ALERT for {reading.printer_id}"
        )

        cloud_sender.send_alert(event)

    elif event_type == "RECOVERY":

        logger.info(
            f"Sending RECOVERY for {reading.printer_id}"
        )

        cloud_sender.send_recovery(event)

    elif event_type == "ALERT_CHANGED":

        previous_alert, new_alert = event

        logger.info(
            f"{reading.printer_id}: "
            f"{previous_alert.type.value} -> {new_alert.type.value}"
        )

        # Close previous alert
        cloud_sender.send_recovery(previous_alert)

        # Raise new alert
        cloud_sender.send_alert(new_alert)

    # ------------------------------------------------
    # Send healthy summaries
    # ------------------------------------------------

    if summary:
        cloud_sender.send_summary(summary)

    logger.info(
        f"Finished processing {reading.printer_id}"
    )

    return {
        "status": "received",
        "printer": reading.printer_id
    }
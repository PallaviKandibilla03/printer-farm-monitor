"""
Alert Manager

Responsible for:

- Duplicate suppression
- Recovery detection
- Active alert tracking
"""

from models import AlertEvent
from logger import logger


class AlertManager:

    def __init__(self):
        self.active_alerts: dict[str, AlertEvent] = {}

    def process(
        self,
        printer_id: str,
        alert: AlertEvent | None,
    ):
        """
        Returns:

        ("NEW_ALERT", alert)
        ("RECOVERY", previous_alert)
        (None, None)
        """

        previous = self.active_alerts.get(printer_id)

        # ----------------------------------
        # Printer Healthy
        # ----------------------------------

        if alert is None:

            if previous:

                logger.info(
                    f"✅ {printer_id} recovered from {previous.type.value}"
                )

                del self.active_alerts[printer_id]

                return (
                    "RECOVERY",
                    previous,
                )

            return (
                None,
                None,
            )

        # ----------------------------------
        # Existing Alert
        # ----------------------------------

        if previous:

            if previous.type == alert.type:

                return (
                    None,
                    None,
                )

        # ----------------------------------
        # New Alert
        # ----------------------------------

        self.active_alerts[printer_id] = alert

        logger.warning(
            f"🚨 {printer_id} | "
            f"{alert.severity.value} | "
            f"{alert.type.value}"
        )

        return (
            "NEW_ALERT",
            alert,
        )
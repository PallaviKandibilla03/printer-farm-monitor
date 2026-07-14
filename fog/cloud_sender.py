"""
Cloud Communication Layer

Placeholder for AWS SQS.
"""

from models import AlertEvent
from logger import logger


class CloudSender:

    def send_alert(
        self,
        alert: AlertEvent,
    ):

        logger.info(
            f"[Cloud] Alert queued: "
            f"{alert.printer_id} | "
            f"{alert.type.value}"
        )

    def send_recovery(
        self,
        alert: AlertEvent,
    ):

        logger.info(
            f"[Cloud] Recovery queued: "
            f"{alert.printer_id}"
        )

    def send_summary(
        self,
        summary,
    ):

        logger.info(
            "[Cloud] Healthy summary queued."
        )
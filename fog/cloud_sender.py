import json
from datetime import datetime

import boto3

from logger import logger
from aws_config import (
    AWS_REGION,
    AWS_PROFILE,
    QUEUE_URL,
)


class CloudSender:

    def __init__(self):

        session = boto3.Session(
            profile_name=AWS_PROFILE,
            region_name=AWS_REGION,
        )

        self.sqs = session.client("sqs")

    # ----------------------------------------------------
    # Send Alert
    # ----------------------------------------------------

    def send_alert(self, alert):

        payload = {
            "event_id": alert.event_id,
            "timestamp": alert.timestamp.isoformat(),
            "source": alert.source.value,
            "version": alert.version,
            "processed": alert.processed,

            "printer_id": alert.printer_id,

            "event": "ALERT",

            "type": alert.type.value,
            "severity": alert.severity.value,
            "message": alert.message,

            "sensor_snapshot": alert.sensor_snapshot,
        }

        response = self.sqs.send_message(
            QueueUrl=QUEUE_URL,
            MessageBody=json.dumps(payload),
        )

        logger.info(
            f"[AWS] ALERT sent ({response['MessageId']})"
        )

    # ----------------------------------------------------
    # Send Recovery
    # ----------------------------------------------------

    def send_recovery(self, alert):

        payload = {
            "event_id": alert.event_id + "-RECOVERY",

            # Recovery is a NEW event
            "timestamp": datetime.utcnow().isoformat(),

            "source": alert.source.value,
            "version": alert.version,
            "processed": False,

            "printer_id": alert.printer_id,

            "event": "RECOVERY",

            "type": alert.type.value,
            "severity": "INFO",

            "message": f"{alert.type.value} recovered successfully.",

            "sensor_snapshot": alert.sensor_snapshot,
        }

        response = self.sqs.send_message(
            QueueUrl=QUEUE_URL,
            MessageBody=json.dumps(payload),
        )

        logger.info(
            f"[AWS] RECOVERY sent ({response['MessageId']})"
        )

    # ----------------------------------------------------
    # Send Summary
    # ----------------------------------------------------

    def send_summary(self, summary):

        response = self.sqs.send_message(
            QueueUrl=QUEUE_URL,
            MessageBody=json.dumps(summary, default=str),
        )

        logger.info(
            f"[AWS] SUMMARY sent ({response['MessageId']})"
        )
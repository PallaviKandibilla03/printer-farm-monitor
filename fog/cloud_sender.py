import json

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

    # ------------------------------------

    def send_alert(self, alert):

        response = self.sqs.send_message(

            QueueUrl=QUEUE_URL,

            MessageBody=json.dumps(
                alert.model_dump(mode="json")
            ),

        )

        logger.info(
            f"[AWS] Alert sent "
            f"{response['MessageId']}"
        )

    # ------------------------------------

    def send_recovery(self, alert):

        payload = {

            "printer_id": alert.printer_id,

            "event": "RECOVERY",

            "timestamp": str(alert.timestamp),

        }

        response = self.sqs.send_message(

            QueueUrl=QUEUE_URL,

            MessageBody=json.dumps(payload),

        )

        logger.info(
            f"[AWS] Recovery sent "
            f"{response['MessageId']}"
        )

    # ------------------------------------

    def send_summary(self, summary):

        response = self.sqs.send_message(

            QueueUrl=QUEUE_URL,

            MessageBody=json.dumps(summary),

        )

        logger.info(
            f"[AWS] Summary sent "
            f"{response['MessageId']}"
        )
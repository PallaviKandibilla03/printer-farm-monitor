import requests
import json
import time

from printer import Printer
from config import NUM_PRINTERS, UPDATE_INTERVAL


def main():
    # Create virtual printers
    printers = [
        Printer(f"P{i}")
        for i in range(1, NUM_PRINTERS + 1)
    ]

    print("=" * 60)
    print("3D Printer Farm Simulator Started")
    print("=" * 60)

    
    while True:

        print("\n---------------- New Sensor Readings ----------------")

        for printer in printers:

            data = printer.generate_sensor_data()

            # Remove failure_mode before sending
            fog_payload = data.copy()
            fog_payload.pop("failure_mode")

            # Print locally
            print(json.dumps(fog_payload, indent=4))

            # Send to Fog Node
            try:
                response = requests.post(
                    "http://127.0.0.1:8000/sensor-data",
                    json=fog_payload,
                    timeout=2
                )

                print(
                    f"✓ Sent {printer.printer_id} "
                    f"({response.status_code})"
                )

            except Exception as e:
                print(f"Fog Node Offline: {e}")

        time.sleep(UPDATE_INTERVAL)


if __name__ == "__main__":
    main()
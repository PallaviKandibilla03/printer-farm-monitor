from fastapi import FastAPI
from models import SensorReading

app = FastAPI(title="3D Printer Fog Node")

# Store the latest reading for each printer
latest_readings = {}


@app.get("/")
def home():
    return {
        "message": "3D Printer Fog Node Running"
    }


@app.post("/sensor-data")
def receive_sensor_data(reading: SensorReading):

    latest_readings[reading.printer_id] = reading

    print("\n====================================")
    print(f"Printer: {reading.printer_id}")
    print(f"Nozzle Temp : {reading.nozzle_temp} °C")
    print(f"Bed Temp    : {reading.bed_temp} °C")
    print(f"Vibration   : {reading.vibration}")
    print(f"Flow        : {reading.flow}")
    print("====================================")

    return {
        "status": "received",
        "printer": reading.printer_id
    }


@app.get("/printers")
def get_printers():
    return latest_readings
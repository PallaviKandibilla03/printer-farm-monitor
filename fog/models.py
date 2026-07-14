from pydantic import BaseModel


class SensorReading(BaseModel):
    timestamp: str
    printer_id: str
    status: str
    progress: int

    nozzle_temp: float
    bed_temp: float
    vibration: float
    flow: float
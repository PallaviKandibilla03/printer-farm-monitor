"""
Application Constants

Shared enumerations used throughout the Fog Node.
"""

from enum import Enum


class EventType(str, Enum):
    NOZZLE_CLOG = "NOZZLE_CLOG"
    FILAMENT_RUNOUT = "FILAMENT_RUNOUT"
    LAYER_SHIFT = "LAYER_SHIFT"
    BED_TEMPERATURE_DRIFT = "BED_TEMPERATURE_DRIFT"


class Severity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class PrinterStatus(str, Enum):
    IDLE = "IDLE"
    PRINTING = "PRINTING"
    PAUSED = "PAUSED"
    ERROR = "ERROR"


class EventSource(str, Enum):
    FOG_NODE = "FOG_NODE"
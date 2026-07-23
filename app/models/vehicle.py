from dataclasses import dataclass


@dataclass
class VehicleCapacity:
    month: str
    branch: str
    operation_type: str
    vehicle_type: str

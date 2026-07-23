from dataclasses import dataclass


@dataclass
class WorkforceCapacity:
    month: str
    branch: str
    function: str
    operational_stage: str

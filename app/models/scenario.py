from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Scenario:
    name: str
    month: str
    created_at: datetime = field(default_factory=datetime.now)
    restrictions: dict[str, float] = field(default_factory=dict)
    aggregate_result: dict[str, float] = field(default_factory=dict)

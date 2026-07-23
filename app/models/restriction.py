from dataclasses import dataclass


@dataclass(frozen=True)
class Restriction:
    client_id: str
    reduction_rate: float

    def __post_init__(self):
        if not 0 <= self.reduction_rate <= 1:
            raise ValueError("reduction_rate deve estar entre 0 e 1.")

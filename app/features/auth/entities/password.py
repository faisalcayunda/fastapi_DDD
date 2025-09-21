from dataclasses import dataclass


@dataclass(frozen=True)
class Password:
    value: str

    def __post_init__(self):
        if len(self.value) < 12:
            raise ValueError("Password too short")
        if self.value.lower() == self.value or self.value.upper() == self.value:
            raise ValueError("Use mixed case")

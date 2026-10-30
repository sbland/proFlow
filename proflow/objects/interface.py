from dataclasses import dataclass


@dataclass(frozen=True)
class I:
    """interface Named Tuple"""

    from_: str
    as_: str = None
    required: bool = False  # If true then is asserted != null on debug mode

    def __repr__(self) -> str:
        return f'I(from_="{self.from_}" as_="{self.as_}")'

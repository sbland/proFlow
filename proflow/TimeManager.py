"""The TimeManager manages the current row index."""
from enum import Enum
from proflow.Objects.Process import Process


class TimeScale(Enum):
    MILLISECOND = 0
    SECOND = 1
    MINUTE = 2
    HOUR = 3
    DAY = 4
    ms = 0
    s = 1
    m = 2
    h = 3
    d = 4


class TimeManager():
    """The TimeManager manages the current row index."""

    def __init__(
        self,
        row_index: int = 0,
        day: int = 0,
        hour: int = 0,
        minute: int = 0,
        second: int = 0,
        millisecond: int = 0,
        row_per: TimeScale = TimeScale.HOUR,
    ):
        self.row_index = row_index
        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = second
        self.millisecond = millisecond
        self.row_per = row_per

    def _advance_row_index(self, by: int = 1):
        """Advances the row index by 1.
        Should use specific advance time step."""
        self.row_index += by

    def advance_row(self, by: int = 1):
        """Advance the row_per value."""
        if self.row_per == TimeScale.DAY:
            self.advance_day(by)
        if self.row_per == TimeScale.HOUR:
            self.advance_hour(by)
        if self.row_per == TimeScale.MINUTE:
            self.advance_minute(by)
        if self.row_per == TimeScale.SECOND:
            self.advance_second(by)
        if self.row_per == TimeScale.DAY:
            self.advance_day(by)

    def advance_day(self, by: int = 1):
        """advance a day by 1 and advance the row index if it is the row_per."""
        self.day += by
        if self.row_per == TimeScale.DAY:
            self._advance_row_index(by)

    def advance_hour(self, by: int = 1):
        """advance a hour by 1 and advance the row index if it is the row_per."""
        self.hour += by
        if self.row_per == TimeScale.HOUR:
            self._advance_row_index(by)
        while self.hour >= 24:
            self.advance_day()
            self.hour = self.hour - 24

    def advance_minute(self, by: int = 1):
        """advance a minute by 1 and advance the row index if it is the row_per."""
        self.minute += by
        if self.row_per == TimeScale.MINUTE:
            self._advance_row_index(by)
        while self.minute >= 60:
            self.advance_hour()
            self.minute = self.minute - 60

    def advance_second(self, by: int = 1):
        """advance a second by 1 and advance the row index if it is the row_per."""
        self.second += by
        if self.row_per == TimeScale.SECOND:
            self._advance_row_index(by)
        while self.second >= 60:
            self.advance_minute()
            self.second = self.second - 60

    def advance_millisecond(self, by: int = 1):
        """advance a millisecond by 1 and advance the row index if it is the row_per."""
        self.millisecond += by
        if self.row_per == TimeScale.MILLISECOND:
            self._advance_row_index(by)
        while self.millisecond >= 1000:
            self.advance_second()
            self.millisecond = self.millisecond - 1000


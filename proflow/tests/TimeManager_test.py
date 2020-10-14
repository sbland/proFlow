from proflow.TimeManager import TimeManager
from ..TimeManager import TimeManager, TimeScale


def test_creating_a_time_manager():
    tm = TimeManager()
    assert tm.row_index == 0
    assert tm.day == 0
    assert tm.hour == 0
    assert tm.minute == 0
    assert tm.second == 0
    assert tm.millisecond == 0


def test_advanceing_time_steps():
    tm = TimeManager(row_per=TimeScale.HOUR)
    assert tm.row_index == 0
    assert tm.day == 0
    assert tm.hour == 0
    assert tm.minute == 0
    assert tm.second == 0
    assert tm.millisecond == 0
    tm._advance_row_index()
    assert tm.row_index == 1
    assert tm.day == 0
    assert tm.hour == 0
    assert tm.minute == 0
    assert tm.second == 0
    assert tm.millisecond == 0
    tm._advance_row_index(3)
    assert tm.row_index == 4
    assert tm.day == 0
    assert tm.hour == 0
    assert tm.minute == 0
    assert tm.second == 0
    assert tm.millisecond == 0
    tm.advance_hour()
    assert tm.row_index == 5
    assert tm.day == 0
    assert tm.hour == 1
    assert tm.minute == 0
    assert tm.second == 0
    assert tm.millisecond == 0
    tm.advance_second()
    assert tm.row_index == 5
    assert tm.day == 0
    assert tm.hour == 1
    assert tm.minute == 0
    assert tm.second == 1
    assert tm.millisecond == 0
    tm.advance_second(59)
    assert tm.row_index == 5
    assert tm.day == 0
    assert tm.hour == 1
    assert tm.minute == 1
    assert tm.second == 0
    assert tm.millisecond == 0
    tm.advance_minute(59)
    assert tm.row_index == 6
    assert tm.day == 0
    assert tm.hour == 2
    assert tm.minute == 0
    assert tm.second == 0
    assert tm.millisecond == 0
    tm.advance_millisecond(1)
    assert tm.row_index == 6
    assert tm.day == 0
    assert tm.hour == 2
    assert tm.minute == 0
    assert tm.second == 0
    assert tm.millisecond == 1
    tm.advance_millisecond(13210)
    assert tm.row_index == 6
    assert tm.day == 0
    assert tm.hour == 2
    assert tm.minute == 0
    assert tm.second == 13
    assert tm.millisecond == 211
    tm.advance_minute(362)
    assert tm.row_index == 12
    assert tm.day == 0
    assert tm.hour == 8
    assert tm.minute == 2
    assert tm.second == 13
    assert tm.millisecond == 211


def test_advanceing_row():
    tm = TimeManager(row_per=TimeScale.HOUR)
    assert tm.row_index == 0
    assert tm.day == 0
    assert tm.hour == 0
    assert tm.minute == 0
    assert tm.second == 0
    assert tm.millisecond == 0
    tm.advance_row()
    assert tm.row_index == 1
    assert tm.day == 0
    assert tm.hour == 1
    assert tm.minute == 0
    assert tm.second == 0
    assert tm.millisecond == 0

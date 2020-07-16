"""Generic helpers related to time data"""


def get_row(day: int, hour: int) -> int:
    """Gets the row index based on day and hour assuming row per hour"""
    row_index: int = (day * 24) + hour
    return row_index

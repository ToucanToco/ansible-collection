from datetime import datetime
import pytest

from plugins.module_utils.date import validate_date
from plugins.module_utils.date import compare_date

@pytest.mark.parametrize("date_str, date_fmt, expected" , [
        pytest.param(
            "2022-08-02T15:00+0200",
            "%Y-%m-%dT%H:%M%z",
            True,
            id="Valid 2022-08-02T15:00+0200"),
        pytest.param(
            "2022-08-02T15:00:30+0200",
            "%Y-%m-%dT%H:%M%z",
            False,
            id="Not valid 2022-08-02T15:00:30+0200"),
    ]
)
def test_validate_date(date_str, date_fmt, expected):
    res = validate_date(date_str, date_fmt)
    assert res == expected

@pytest.mark.parametrize("a, b, attributes, expected" , [
        pytest.param(
            datetime(2017, 11, 28, 23, 55, 59),
            datetime(2017, 11, 28, 23, 55, 59),
            ["year", "month", "day", "hour", "minute", "second"],
            True,
            id="Exactly same dates"),
        pytest.param(
            datetime(2017, 11, 28, 23, 55, 59),
            datetime(2022, 12, 21, 23, 55, 59),
            ["year", "month", "day", "hour", "minute", "second"],
            False,
            id="Different dates"),
        pytest.param(
            datetime(2017, 11, 28, 23, 55, 59),
            datetime(2017, 11, 28, 23, 55, 30),
            ["year", "month", "day", "hour", "minute"],
            True,
            id="Seconds different but not compared"),
    ]
)
def test_compare_date(a, b, attributes, expected):
    res = compare_date(a, b, attributes)
    assert res == expected

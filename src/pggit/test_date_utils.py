import pytest
import date_utils
from zoneinfo import ZoneInfo


testcases = [
    (
        "2023-11-12 13:22:33.123421+08:00",
        ZoneInfo("Asia/Shanghai"),
        "2023-11-12 13:22:33.123421+08:00",
    ),
    (
        "2023-11-12 13:22:33.123+08:00",
        ZoneInfo("Asia/Shanghai"),
        "2023-11-12 13:22:33.123000+08:00",
    ),
    (
        "2023-11-12 13:22:33.+08:00",
        ZoneInfo("Asia/Shanghai"),
        "2023-11-12 13:22:33+08:00",
    ),
    ("2023-11-12 13:22+08:00", ZoneInfo("Asia/Shanghai"), "2023-11-12 13:22:00+08:00"),
    ("2023-11-12 13+08:00", ZoneInfo("Asia/Shanghai"), "2023-11-12 13:00:00+08:00"),
    (
        "2023/11/12 13:22:33.123421+08:00",
        ZoneInfo("Asia/Shanghai"),
        "2023-11-12 13:22:33.123421+08:00",
    ),
    (
        "2023-11-12 13:22:33.123421",
        ZoneInfo("Asia/Shanghai"),
        "2023-11-12 21:22:33.123421+08:00",
    ),
    (
        "2023-11-12 13:22:33.123",
        ZoneInfo("Asia/Shanghai"),
        "2023-11-12 21:22:33.123000+08:00",
    ),
    (
        "2023-11-12 13:22:33.",
        ZoneInfo("Asia/Shanghai"),
        "2023-11-12 21:22:33+08:00",
    ),
    ("2023-11-12 13:22", ZoneInfo("Asia/Shanghai"), "2023-11-12 21:22:00+08:00"),
    ("2023-11-12 13", ZoneInfo("Asia/Shanghai"), "2023-11-12 21:00:00+08:00"),
    ("2023-11-12", ZoneInfo("Asia/Shanghai"), "2023-11-12 08:00:00+08:00"),
    (
        "2023/11/12 13:22:33.123421",
        ZoneInfo("Asia/Shanghai"),
        "2023-11-12 21:22:33.123421+08:00",
    ),
]


@pytest.mark.parametrize(["datestr", "tzinfo", "resultstr"], testcases)
def test_dateparser(datestr: str, tzinfo: ZoneInfo, resultstr: str):
    date = date_utils.dateparser(datestr, tzinfo)
    assert date.__str__() == resultstr


def test_beijing():
    date = date_utils.beijing()
    assert date.tzinfo == ZoneInfo("Asia/Shanghai")

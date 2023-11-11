"""
this module provides some tools for date processing

"""

from datetime import datetime
from zoneinfo import ZoneInfo
from dateutil import parser


def beijing():
    """get beijing time"""
    return datetime.now(tz=ZoneInfo("Asia/Shanghai"))


def dateparser(date: str, tz: ZoneInfo = ZoneInfo("Asia/Shanghai")):
    """parse date from a format date string

    Args:
        date: string format datetime
        tz: target timezone will transfer to

    Returns:
        datetime: a datetime object with beijing timezone,
            a none timezone date string will be regarded
            as UTC timezone
    """

    try:
        result = parser.parse(date)
        if result:
            if not result.tzinfo:
                result = result.replace(tzinfo=ZoneInfo("UTC"))
            result = result.astimezone(tz)
    except Exception as e:
        print(f"[dateparser] error: {e}")
        result = None
    return result

import logging
from datetime import datetime

logger = logging.getLogger(__name__)
DATE_FORMAT = '%a, %d %b %Y %H:%M:%S %z'


def string_to_datetime(string: str) -> datetime:
    return datetime.strptime(string, DATE_FORMAT)


def datetime_to_string(date: datetime) -> str:
    return date.strftime(DATE_FORMAT)


def normalize_timezone(date_: str) -> str:
    time_zones = {
        'EST': '-0500',
        'PDT': '-0700',
        'PST': '-0800',
    }
    time_zone = date_.rsplit(' ', 1)[-1]
    if time_zone in time_zones:
        normalize_date = date_.replace(time_zone, time_zones[time_zone])
        logger.info(f'Date {date_} changed to {normalize_date}')
        return normalize_date
    return date_

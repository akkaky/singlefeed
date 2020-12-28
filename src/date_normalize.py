from datetime import datetime


DATE_FORMAT = '%a, %d %b %Y %H:%M:%S %z'


def string_to_datetime(string: str) -> datetime:
    return datetime.strptime(string, DATE_FORMAT)


def normalize_timezone(date_: str) -> str:
    time_zones = {
        'EST': '-0500',
        'PDT': '-0700',
        'PST': '-0800',
    }
    time_zone = date_.rsplit(' ', 1)[-1]
    if time_zone in time_zones:
        return date_.replace(time_zone, time_zones[time_zone])
    return date_

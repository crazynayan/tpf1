from datetime import datetime, timedelta
from typing import Tuple

from config import config
from utils.data_type import DataType
from utils.errors import UcdrError


def date_to_pars(date_bytes: bytearray) -> Tuple[int, int]:
    # Date to PARS day number. 03OCT (2019) -> 4CB0,??
    today = datetime(year=datetime.today().year, month=datetime.today().month, day=datetime.today().day)
    date_str = DataType('X', bytes=date_bytes).decode
    date = datetime.strptime(date_str, '%d%b')
    date = date.replace(year=today.year)
    days_from_today = (date - today).days
    past_days_allowed = config.GROSS_DAYS - (datetime(today.year, 12, 31) - datetime(today.year, 1, 1)).days
    if days_from_today < past_days_allowed:
        date = date.replace(year=date.year + 1)
    return (date - config.PARS_DAY_1).days, (date - today).days


def pars_to_date(days_from_start: int) -> bytearray:
    if not 0 <= days_from_start <= 0x7FFF:
        raise UcdrError
    date = config.PARS_DAY_1 + timedelta(days=days_from_start)
    date_str = date.strftime('%d%b').upper()
    date_bytes = DataType('C', input=date_str).to_bytes()
    return date_bytes

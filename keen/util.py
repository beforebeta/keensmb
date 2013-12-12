from datetime import date
from datetime import datetime
from datetime import timedelta
import calendar

def get_first_day_of_month_as_dt():
    """
    get today as a datetime object instead of a date object
    the hours, minutes and seconds hand is just going to be 0
    """
    today = date.today()
    return datetime.combine(today - timedelta(days = today.day-1), datetime.min.time())

def get_last_day_of_month_as_dt():
    today = date.today()
    last_day = calendar.monthrange(today.year, today.month)[1]
    return datetime(year=today.year, month=today.month, day=last_day, hour=23, minute=59, second=59)
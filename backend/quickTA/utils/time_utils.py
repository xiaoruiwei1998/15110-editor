import pytz
from datetime import datetime, date
from django.utils import timezone, dateparse

def now():
    return datetime.now()

def today():
    return date.today()

def convert_start_end_date(start_date, end_date):
    
    start_year = int(start_date.split("-")[0])
    start_month = int(start_date.split("-")[1])
    start_day = int(start_date.split("-")[2])   

    end_year = int(end_date.split("-")[0])
    end_month = int(end_date.split("-")[1])
    end_day = int(end_date.split("-")[2])

    start_date = datetime(start_year, start_month, start_day)
    end_date = datetime(end_year, end_month, end_day)
    
    return start_date, end_date

def nowDateTimeCsvStr():
    return timezone.now().strftime("%Y-%m-%d_%H-%M-%S")

def get_server_time(time, location):
    return time.astimezone(pytz.timezone(location)).isoformat() + "[" + location + "]"
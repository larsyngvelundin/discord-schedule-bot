from datetime import datetime, timedelta
import os

import discord
from discord.ext import tasks
from icalendar import Calendar
import pytz
import requests
from dotenv import load_dotenv

load_dotenv()
calendar_link = os.environ['CALENDARLINK']
discord_key = os.environ['DISCORD']



def get_upcoming_events(url, days=100):
    req = requests.get(url)
    if req.status_code == 200:
        print(req.text)
        gcal = Calendar.from_ical(req.text)
        current_time = datetime.now(pytz.utc)
        end_time = current_time + timedelta(days=days)

        for component in gcal.walk():
            if component.name == "VEVENT":
                dtstart = component.get('dtstart').dt
                if isinstance(dtstart, datetime):
                    dtstart = dtstart.astimezone(pytz.utc)
                else:
                    dtstart = datetime.combine(dtstart, datetime.min.time(), tzinfo=pytz.utc)
                if current_time < dtstart < end_time:
                    summary = component.get('summary')
                    print(f"Event: {summary}")
                    print(f"Starts: {dtstart.isoformat()}")
                    
    else:
        print('Failed to fetch the calendar data')

get_upcoming_events(calendar_link)
from datetime import datetime, timedelta
import os
from time import sleep

import discord
from discord.ext import tasks
from icalendar import Calendar
import pytz
import requests
from dotenv import load_dotenv

load_dotenv()
calendar_link = os.environ['CALENDARLINK']
discord_key = os.environ['DISCORD']

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

channel_id = os.environ['CHANNELID']
message_prefix = "Upcoming lectures:"



async def get_upcoming_events(days=100):
    schedule_string = ""
    req = requests.get(calendar_link)
    if req.status_code == 200:
        print(req.text)
        gcal = Calendar.from_ical(req.text)
        current_time = datetime.now(pytz.utc)
        end_time = current_time + timedelta(days=days)

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        schedule_string += f'\n\n'
        for component in gcal.walk():
            if component.name == "VEVENT":
                # print(component)
                # print(component.get('DESCRIPTION'))

                event_description = component.get('DESCRIPTION')
                if event_description.find("Mötes-") != -1:
                    link_start = event_description.find("Anslut till mötet nu") + 20
                    link_end = event_description.find("Mötes-") - 1
                else:
                    link_start = event_description.find("Join the meeting now<") + 20
                    link_end = event_description.find("Meeting ID:") - 1
                event_link = event_description[link_start:link_end]
                # print(f"event_link {event_link}")

                dtstart = component.get('dtstart').dt
                dtend = component.get('dtend').dt
                if isinstance(dtstart, datetime) and isinstance(dtend, datetime):
                    dtstart = dtstart.astimezone(pytz.timezone("CET"))
                    dtend = dtend.astimezone(pytz.timezone("CET"))
                else:
                    dtstart = datetime.combine(dtstart, datetime.min.time(), tzinfo=pytz.timezone("CET"))
                    dtend = datetime.combine(dtend, datetime.min.time(), tzinfo=pytz.timezone("CET"))
                if current_time < dtstart < end_time:
                    event_name = component.get('summary')
                    # print(f"Time: {dtstart}")
                    # print(f"Name: {summary}")
                    # print(f"Link: {event_link}")
                    # print(f"Event: {summary}")
                    # print(f"Starts: {dtstart.isoformat()}")
                    event_date = dtstart.strftime("%Y-%m-%d")
                    event_start = dtstart.strftime("%H:%M")
                    event_end = dtend.strftime("%H:%M")
                    # print(f"{event_date} {event_start}-{event_end} \n")
                    # test = input("stop")
                    schedule_string +=  f"{event_date} {event_start}-{event_end} \n"
                    schedule_string += event_name + "\n"
                    schedule_string += f"[Meeting link]({event_link})"
                    # schedule_string += event_name + "\n"
                    schedule_string += "\n\n"
                    print(f"schedelu length: {len(schedule_string)}")
                    if(len(schedule_string) > 1700):
                        schedule_string += f'(Last update: {now_str})'
                        return schedule_string
        
        schedule_string += f'(Last update: {now_str})'
        return schedule_string

    else:
        return None
        print('Failed to fetch the calendar data')

# get_upcoming_events(calendar_link)

@ client.event
async def on_ready():
    channel = client.get_channel(int(channel_id))
    last_message_id = await get_last_message(channel)
    await post_schedule(last_message_id, channel)
    print(f"Last message: {last_message_id}")

async def get_last_message(channel):
    if channel:
        async for message in channel.history(limit=1):
            last_message_id = message.id
            return last_message_id
        else:
            return None
    else:
        return None

# async def get_schedule_string():
#     schedule_string = ""

#     return schedule_string

async def post_schedule(last_message_id, channel):
    if not last_message_id:
        await create_message(channel)
        last_message_id = await get_last_message(channel)
    schedule_string = await get_upcoming_events()
    message_to_edit = await channel.fetch_message(last_message_id)
    await message_to_edit.edit(content=f"{message_prefix}{schedule_string}")

async def create_message(channel):
    try:
        async with channel.typing():
            await channel.send(message_prefix)
    except Exception as e:
        print(e)
        print("sleeping 2 seconds and trying again")
        sleep(2)
        await create_message(channel)

client.run(discord_key)
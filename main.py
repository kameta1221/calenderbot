#  -----------------------------------------------------------------------------
#   <main.py>
#    - aaaa
#  -----------------------------------------------------------------------------
#   Version 0 (2022/05/07 8:56)
#    -
#  -----------------------------------------------------------------------------
#   (C) 2022 masahiro nishimura. All rights reserved.
#  -----------------------------------------------------------------------------

import json
import os

import discord
import traceback
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

with open('config.json', 'r', encoding="utf8") as f:
    config = json.load(f)
    discordToken = config['discord'].get('token')
    calendarText = config['calendar'].get('calendar_text')
    listText = config['calendar'].get('list_text')
    addEventText = config['calendar'].get('add_event_text')
    addLongEventText = config['calendar'].get('add_long_event_text')
    deleteEventText = config['calendar'].get('delete_text')

DISCORDBOT_TOKEN = os.environ["DISCORDBOT_TOKEN"]

# bot = commands.Bot(command_prefix=".", intents=discord_intents)

cogslist = [
    'cogs.calendar'
]


class MyBot(commands.Bot):

    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix, intents=intents)

    async def on_ready(self):
        print(f"Logged in as {bot.user.name}({bot.user.id})")
        # await client.change_presence(activity=discord.Game(name="", type=1))
        print(discord.__version__)
        for cog in cogslist:
            try:
                await self.load_extension(cog)
            except Exception:
                traceback.print_exc()


# @bot.event
# async def on_message(message):
#     content = message.content
#
#     if content == calendarText:
#         logic = CalendarLogic()
#         result = logic.calendarUrl()
#
#     if content == listText:
#         logic = CalendarLogic()
#         result = logic.get()
#
#     elif re.search(addEventText, content):
#         event = content.replace(addEventText, '')
#         logic = CalendarLogic()
#         logic.insert(event)
#
#     elif re.search(addLongEventText, content):
#         event = content.replace(addLongEventText, '')
#         logic = CalendarLogic()
#         logic.insertLongEvent(event)
#
#     elif re.search(deleteEventText, content):
#         eventId = content.replace(deleteEventText, '')
#         logic = CalendarLogic()
#         logic.delete(eventId)

if __name__ == '__main__':
    discord_intents = discord.Intents.all()
    bot = MyBot(command_prefix='!', intents=discord_intents)
    bot.run(DISCORDBOT_TOKEN)

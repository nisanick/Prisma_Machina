import asyncio
import random
from datetime import datetime

import discord
from discord.ext import commands

from config import *
import database


class Utils:
    def __init__(self, bot):
        self.bot = bot

    async def on_ready(self):
        #await self.timer(1)
        pass

    @commands.command(aliases=['what is the time'])
    async def time(self, ctx):
        year = datetime.now().timetuple().tm_year
        now = datetime.utcnow().replace(year=(year + 1286)).strftime("%H:%M %d %b %Y")
        await ctx.send(now)

    async def on_member_join(self, member: discord.Member):
        # TODO - where is the message going? no magical numbers in code
        channel = self.bot.get_channel(322456259897065472)
        await channel.send('Welcome to Prismatic Imperium {}'.format(member.mention))

    async def on_member_remove(self, member):
        channel = self.bot.get_channel(322456259897065472)
        await channel.send('{} left the server'.format(member.mention))

    async def timer(self, delay):
        await asyncio.sleep(delay)
        print('timer')
        db = await database.Database.get_connection()
        query_event = "SELECT event_id, event_type FROM schedule WHERE event_time <= %(when)s AND done = FALSE"
        query_update = "UPDATE schedule SET done = TRUE WHERE event_id = %(id)s"
        data = {
            'when': datetime.utcnow(),
            'id': 0
        }
        events = db.cursor(buffered=True)
        events.execute(query_event, data)
        for event_id, event_type in events:
            data['id'] = event_id
            if event_type is 0:
                await self.timed_message()
            db.cursor().execute(query_update, data)
            db.commit()
        await self.timer(60)

    async def timed_message(self):
        db = Database.get_connection()
        query_message = "SELECT message_content FROM messages ORDER BY RAND() LIMIT 1"
        query_insert = "INSERT INTO schedule (done, event_type, event_time) VALUES (FALSE, 0, %(when)s)"
        new_delay = random.randint(43200, 86400)
        stamp = datetime.utcnow().timestamp() + new_delay
        print(datetime.fromtimestamp(stamp))
        data = {
            'when': datetime.fromtimestamp(stamp)
        }
        message = db.cursor(buffered=True)
        message.execute(query_message)
        content = message.fetchone()[0]
        # TODO - maybe not more than 1 channel
        for channel_id in TIMED_MESSAGE_CHANNELS:
            channel = self.bot.get_channel(channel_id)
            await channel.send(content)
        db.cursor().execute(query_insert, data)
        db.commit()

    async def on_message(self, message):
        """content = message.content.lower()
        for word in PROFANITY:
            if word in content:
                await message.channel.send("Hey! Mind your tongue {}".format(message.author.mention))"""
        print(message.content)

    @commands.command()
    async def add(self, ctx, *args):
        message = args[0]
        db = Database.get_connection()
        query = "INSERT INTO messages (message_content) VALUES (%(message)s)"
        cursor = db.cursor()
        values = {
            'message': message
        }
        cursor.execute(query, values)
        db.commit()
        cursor.close()
        await ctx.send("Message added")


def setup(bot):
    bot.add_cog(Utils(bot))

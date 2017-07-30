from discord.ext import commands
import asyncio
from database import Database
from datetime import datetime
import config
import re
import discord
import random


class Timer:
    def __init__(self, bot):
        self.bot = bot
        self.execute = True
        self.step = 5
        self.task = self.bot.loop.create_task(self.timer())

    async def timer(self):
        await asyncio.sleep(10)
        while self.execute:
            await self.check_events()
            await asyncio.sleep(self.step)

    @commands.command()
    async def stop(self, ctx):
        self.execute = False

    async def check_events(self):
        """ event types are as follows:
            2 - The Daily Chat
        """
        event_select = "SELECT event_id, event_type FROM schedule WHERE done = FALSE AND event_time <= $1"
        event_update = "UPDATE schedule SET done = TRUE WHERE event_id = $1"
        db = await Database.get_connection(self.bot.loop)
        async with db.transaction():
            async for (event_id, event_type) in db.cursor(event_select, datetime.utcnow()):
                # The Daily Chat
                if event_type == 2:
                    await self.send_article(event_type, True)
                await db.execute(event_update, event_id)
        await Database.close_connection(db)

    async def send_article(self, event_type, schedule=False):
        count_select = "SELECT min(used) as usage FROM messages WHERE message_type = $1"
        message_select = ("SELECT message_id, message_title, message_author, message_content, message_footer, message_color "
                          "FROM messages WHERE message_type = $1 AND used = $2 ORDER BY "
                          "floor(random()*(SELECT count(*) FROM messages WHERE used = $2)) LIMIT 1")
        event_insert = "INSERT INTO schedule(event_time, event_type) VALUES ($1, $2)"
        message_update = "UPDATE messages SET used = messages.used + 1 WHERE message_id = $1"
        stamp = datetime.utcnow().timestamp()
        if event_type == 1:
            thumbnail = 'https://prismaticimperiumdotcom.files.wordpress.com/2016/02/aliciamellor.png?w=723'
            time = datetime.fromtimestamp(stamp + random.randint(21600, 43200))
        else:
            return
        event_values = [
            time,
            event_type
        ]
        db = await Database.get_connection(self.bot.loop)
        async with db.transaction():
            row = await db.fetchrow(count_select, event_type)
            values = [
                event_type,
                row['usage']
            ]
            async for (message_id, message_title, message_author, message_content, message_footer, message_color) in db.cursor(message_select, *values):
                message_text = self.replace_emotes(message_content)
                channel = self.bot.get_channel(config.RP_CHANNEL)
                embed = discord.Embed(title=message_title, description=message_text, color=message_color)
                embed.set_author(name=message_author)
                embed.set_thumbnail(url=thumbnail)
                embed.set_footer(text=message_footer)
                await channel.send(embed=embed)
                await db.execute(message_update, message_id)
                if schedule:
                    await db.execute(event_insert, *event_values)
        await Database.close_connection(db)

    def replace_emotes(self, text: str) -> str:
        emote_string = ":[A-z]+:"
        return_text = text
        expression = re.compile(emote_string)
        result = expression.findall(text)
        for word in result:
            emote_name = word[1:-1]
            emote = word
            for emoji in self.bot.emojis:
                if emoji.name == emote_name.lower():
                    emote = emoji
            return_text = return_text.replace(word, "<:{}:{}>".format(emote.name, emote.id))
        return return_text


def setup(bot):
    bot.add_cog(Timer(bot))

from discord.ext import commands
import asyncio
from database import Database
from datetime import datetime
import config
import re
import discord
import random
import checks
from web import Web
from data import links


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

    @commands.command(hidden=True)
    @commands.check(checks.can_manage_bot)
    @commands.check(checks.in_admin_channel)
    async def stop(self, ctx):
        self.execute = False

    async def check_events(self):
        """ event types are as follows:
            2 - The Daily Chat
            0 - article check
        """
        event_select = "SELECT event_id, event_type, event_special FROM schedule WHERE done = FALSE AND event_time <= $1"
        event_update = "UPDATE schedule SET done = TRUE WHERE event_id = $1"
        db = await Database.get_connection(self.bot.loop)
        async with db.transaction():
            async for (event_id, event_type, event_special) in db.cursor(event_select, datetime.utcnow()):
                # The Daily Chat
                if event_type == 2:
                    await self.send_article(event_type, True)
                # article check
                if event_type == 0:
                    await self.check_articles(event_special)
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
        if event_type == 2:
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
                if emoji.name.lower() == emote_name.lower():
                    emote = emoji
            return_text = return_text.replace(word, "<:{}:{}>".format(emote.name, emote.id))

        return return_text

    async def check_articles(self, event_special):
        response = await Web.get_response(links.last_article_link)
        event_insert = "INSERT INTO schedule(event_time, event_type, event_special) VALUES ($1, 0, $2)"
        if response['last_newsID'] != event_special:
            headers = await Web.get_site_header(response['last_newsID'])
            embed = discord.Embed(title=headers['title'], url=headers['url'], description=headers['description'], color=discord.Colour.greyple())
            embed.set_thumbnail(url=headers['image'])
            channel = self.bot.get_channel(config.NEWS_CHANNEL)
            await channel.send("There is a new article on our website!!", embed=embed)
        db = await Database.get_connection(self.bot.loop)
        async with db.transaction():
            stamp = datetime.utcnow().timestamp()
            values = [
                datetime.fromtimestamp(stamp + 600),
                response['last_newsID']
            ]
            await db.execute(event_insert, *values)
        await Database.close_connection(db)


def setup(bot):
    bot.add_cog(Timer(bot))

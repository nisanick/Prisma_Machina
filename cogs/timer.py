import asyncio
import random
from datetime import datetime
from datetime import timedelta

import discord
from discord.ext import commands

from TextChecker import TextChecker
import checks
import config
from data import links
from database import Database
from web import Web
import urllib.parse


class Timer(commands.Cog):
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
            0 - Website article
            1 - Probation
            2 - RP message
        """
        event_select = "SELECT event_id, event_type, event_special FROM schedule WHERE done = FALSE AND event_time <= $1"
        event_update = "UPDATE schedule SET done = TRUE WHERE event_id = $1"

        db = await Database.get_connection(self.bot.loop)
        async with db.transaction():
            async for (event_id, event_type, event_special) in db.cursor(event_select, datetime.utcnow()):

                # Website article
                if event_type == 0:
                    await self.check_articles(event_special)

                # Probation
                if event_type == 1:
                    await self.probation(event_special)

                # RP message
                elif event_type == 2:
                    await self.send_article(int(event_special), True)

                await db.execute(event_update, event_id)
        await Database.close_connection(db)

    async def send_article(self, event_type, schedule=False):
        count_select = "SELECT min(used) as usage FROM messages WHERE message_type = $1"
        message_select = ("SELECT message_id, message_title, message_author, message_content, message_footer, message_color "
                          "FROM messages WHERE message_type = $1 AND used = $2 ORDER BY "
                          "floor(random()*(SELECT count(*) FROM messages WHERE used = $2)) LIMIT 1")
        event_insert = "INSERT INTO schedule(event_time, event_type, event_special) VALUES ($1, 2, $2)"
        message_update = "UPDATE messages SET used = messages.used + 1 WHERE message_id = $1"
        today = datetime.utcnow()
        tomorrow = today + timedelta(days=1)
        in_a_week = today + timedelta(days=7)

        if event_type == 1:
            thumbnail = 'TheDailyChat.png'
            time = tomorrow.replace(hour=13, minute=0, second=0, microsecond=0)
        elif event_type == 2:
            thumbnail = 'GetTheTruth.png'
            time = tomorrow.replace(hour=18, minute=0, second=0, microsecond=0)
        elif event_type == 3:
            thumbnail = 'Forculus_Chronometry.png'
            time = in_a_week.replace(hour=10, minute=0, second=0, microsecond=0)
        elif event_type == 4:
            thumbnail = 'Vector.jpg'
            time = tomorrow.replace(hour=22, minute=0, second=0, microsecond=0)
        elif event_type == 5:
            thumbnail = 'PrismaticMediaNews.png'
            time = in_a_week.replace(hour=0, minute=0, second=0, microsecond=0)
        elif event_type == 6:
            thumbnail = 'GoodMorningCubeo.png'
            time = in_a_week.replace(hour=8, minute=0, second=0, microsecond=0)
        else:
            return
        event_values = [
            time,
            str(event_type)
        ]

        db = await Database.get_connection(self.bot.loop)
        async with db.transaction():
            row = await db.fetchrow(count_select, event_type)
            values = [
                event_type,
                row['usage']
            ]

            async for (message_id, message_title, message_author, message_content, message_footer, message_color) in db.cursor(message_select, *values):
                message_text = TextChecker.replace_emotes(message_content, self.bot)
                channel = self.bot.get_channel(config.RP_CHANNEL)
                # channel = self.bot.get_channel(config.RP_CHANNEL)
                embed = discord.Embed(title=message_title, description=message_text, color=message_color)
                embed.set_author(name=message_author)
                embed.set_thumbnail(url='http://nisanick.com/pictures/{}'.format(thumbnail))
                embed.set_footer(text=message_footer)
                await channel.send(embed=embed)
                await db.execute(message_update, message_id)

                if schedule:
                    await db.execute(event_insert, *event_values)
        await Database.close_connection(db)

    async def check_articles(self, event_special):
        response = await Web.get_response(links.last_article_link)
        event_insert = "INSERT INTO schedule(event_time, event_type, event_special) VALUES ($1, 0, $2)"

        if response['last_newsID'] != event_special:
            headers = await Web.get_site_header(response['last_newsID'])
            embed = discord.Embed(title=headers['title'], url=headers['url'], description=headers['description'], color=discord.Colour.greyple())
            image = urllib.parse.urlparse(headers['image'])
            embed.set_image(url="{}://{}{}".format(image.scheme, image.netloc, urllib.parse.quote(image.path)))
            channel = self.bot.get_channel(config.NEWS_CHANNEL)
            await channel.send("There is a new article on our website!!", embed=embed)

        db = await Database.get_connection(self.bot.loop)
        async with db.transaction():
            stamp = datetime.utcnow().timestamp()
            values = [
                datetime.fromtimestamp(stamp + 3600),
                response['last_newsID']
            ]
            await db.execute(event_insert, *values)
        await Database.close_connection(db)

    async def probation(self, member):
        channel = self.bot.get_channel(int(config.ADMINISTRATION_CHANNEL))
        await channel.send("Probation for <@{}> expired. <@{}>".format(member, 205504598792863744))


def setup(bot):
    bot.add_cog(Timer(bot))

import discord
from discord.ext import commands
from datetime import datetime
import asyncio
import random


class Utils:
    def __init__(self, bot):
        self.bot = bot

    async def on_ready(self):
        await self.timed_message(5)
        pass

    @commands.command()
    async def time(self):
        year = datetime.now().timetuple().tm_year
        now = datetime.utcnow().replace(year=(year + 1286)).strftime("%H:%M %d %b %Y")
        await self.bot.say(now)

    async def on_member_join(self, member: discord.Member):
        await self.bot.send_message(self.bot.get_channel('322456259897065472'), 'Welcome to Prismatic Imperium {}'.format(member.mention))

    async def on_member_remove(self, member):
        await self.bot.send_message(self.bot.get_channel('322456187436138498'),
                                    '{} left the server'.format(member.mention))

    async def timed_message(self, delay):
        await asyncio.sleep(delay)
        await self.bot.send_message(self.bot.get_channel('322456259897065472'),
                                    "timed message {}".format(datetime.utcnow()))
        new_delay = random.randint(36000, 50400)
        print(new_delay)
        await self.timed_message(new_delay)


def setup(bot):
    bot.add_cog(Utils(bot))

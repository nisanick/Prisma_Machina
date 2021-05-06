# coding=utf-8
import discord
from discord.ext import commands
import random
from datetime import datetime

import config
from web import Web
import math

default_chance = 600


class Fun(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.limit = default_chance

    @commands.command()
    async def awesomenessof(self, ctx, who):
        """
        Tells you how awesome you are in comparison to Wisewolf.
        """
        options = [
            'is Exceeding expectations',
            'went down by 1 point since last time',
            'needs to be 20% higher',
            'is 42',
            'is Over safety limits',
            'is Leeking from systems',
            'is Hidden under the sofa',
            'is Defined in 345.654.655 dictionaries as Stunning',
            'is Traveling at warp 6.9',
            'can get to Beagle Point in less than 5 parsecs',

        ]
        member = await commands.MemberConverter().convert(ctx, who)
        if member.id == 205504598792863744:
            await ctx.send("Awesomeness of Wisewolf {}".format(random.choice(options)))
        elif member.id == 186829544764866560:  # Techeron
            await ctx.send("BY ACHENAR... you compared to almighty Wisewolf? Please..")
        elif member.id == 152527690291871745:  # Ryan
            await ctx.send("[REDACTED BY ADMINISTRATION - Classified information]")
        elif member.id == 360543179591909397:  # Bear
            await ctx.send("Is Rupey awesome or is it just a little lie? Tune into Prismatic Media News to find out!")
        else:
            if datetime.strptime('1.4.{}'.format(datetime.utcnow().year), '%d.%m.%Y') == datetime.utcnow():
                await ctx.send("Everyone is better than Wisewolf")
            else:
                await ctx.send("You will never be as awesome as Wisewolf")

    @commands.command()
    async def report(self, ctx):
        """Reports the incident directly to proper authorities!"""
        if datetime.strptime('1.4.{}'.format(datetime.utcnow().year), '%d.%m.%Y') == datetime.utcnow():
            await ctx.send("{} was reported to proper authorities!".format(ctx.author.nick or ctx.author.name))
        else:
            await ctx.send("This incident was reported to proper authorities!")
        if not isinstance(ctx.channel, discord.DMChannel):
            await ctx.message.delete()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        number = random.randint(1, 1000)
        
        if isinstance(message.channel, discord.DMChannel):
            return

        if '💎' in message.channel.name or 'rp-script' in message.channel.name:
            self.limit = self.limit - 10
            return

        if "hi bot" in message.content.lower():
            emoji = self.bot.get_emoji(340954397502865409)
            if emoji:
                await message.add_reaction(emoji)

        if number > self.limit:
            if "tharg" in message.content.lower():
                emoji = discord.utils.get(message.guild.emojis, name='tinfoilhat')
                await message.add_reaction(emoji or '👽')
                self.limit = default_chance

            if message.author.id == 186829544764866560 and "by" in message.content.lower() \
                    and "achenar" in message.content.lower():
                await message.add_reaction(random.choice(['🍺', '🍷', '🍸', '🍹', '🥃']))
                self.limit = default_chance

            if "trumble" in message.content.lower():
                emoji = discord.utils.get(message.guild.emojis, name='Trumble')
                await message.add_reaction(emoji)
                self.limit = default_chance

            if "Vigor" in message.content:
                emoji = discord.utils.get(message.guild.emojis, name='vigor')
                await message.add_reaction(emoji)
                self.limit = default_chance

            if "Sight" in message.content:
                emoji = discord.utils.get(message.guild.emojis, name='sight')
                await message.add_reaction(emoji)
                self.limit = default_chance

            if "Mind" in message.content:
                emoji = discord.utils.get(message.guild.emojis, name='mind')
                await message.add_reaction(emoji)
                self.limit = default_chance

            if "Aurora" in message.content:
                emoji = discord.utils.get(message.guild.emojis, name='aurora')
                await message.add_reaction(emoji)
                self.limit = default_chance

            if "aisling" in message.content.lower() or "duval" in message.content.lower():
                emoji = discord.utils.get(message.guild.emojis, name='aislingduval')
                await message.add_reaction(emoji)
                self.limit = default_chance

            if "kumo" in message.content.lower() or "burger" in message.content.lower():
                emoji = discord.utils.get(message.guild.emojis, name='KumoBurger')
                await message.add_reaction(emoji)
                self.limit = default_chance
        else:
            self.limit = self.limit - 10


def setup(bot: commands.Bot):
    bot.add_cog(Fun(bot))

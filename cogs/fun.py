import discord
from discord.ext import commands
import random


class Fun:
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(hidden=True)
    async def awesomenessof(self, ctx, who):
        options = [
            'is Exceeding expectations',
            'Went down by 1 point since last time',
            'Needs to be 20% higher',
            'is 43',
            'is Over safety limits',
            'is Leeking from systems',
            'is Hidden under the sofa',
            'is Defined in 345.654.655 dictionaries as Stunning',
            'is Traveling at warp 6.9',
            'Can get to Beagle Point in less than 5 parsecs',

        ]
        member = await commands.MemberConverter().convert(ctx, who)
        if member.id == 205504598792863744:
            await ctx.send("Awesomeness of Wisewolf {}".format(random.choice(options)))
        else:
            await ctx.send("You will never be as awesome as Wisewolf")

    async def on_message(self, message: discord.Message):
        if message.author.id == 186829544764866560 and message.content.lower().__contains__("by achenar"):
            await message.add_reaction(random.choice(['🍺', '🍷', '🍸', '🍹', '🥃']))

        if message.content.lower().__contains__("thargoid"):
            emoji = discord.utils.get(message.guild.emojis, name='tinfoilhat')
            await message.add_reaction(emoji or '👽')


def setup(bot: commands.Bot):
    bot.add_cog(Fun(bot))

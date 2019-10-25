# coding=utf-8
import discord
from discord.ext import commands
import random
from datetime import datetime

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
        elif member.id == 186829544764866560:  # Techeron
            await ctx.send("BY ACHENAR... you compared to almighty Wisewolf? Please")
        elif member.id == 351706853153046549:  # Ryan
            await ctx.send("[REDACTED BY ADMINISTRATION - Classified information]")
        elif member.id == 360543179591909397:  # Bear
            await ctx.send("Rupey is as awesome as a teacher can be.")
        else:
            if datetime.strptime('1.4.{}'.format(datetime.utcnow().year), '%d.%m.%Y') == datetime.utcnow():
                await ctx.send("Everyone is better than Wisewolf")
            else:
                await ctx.send("You will never be as awesome as Wisewolf")

    @commands.command(hidden=True)
    async def report(self, ctx, *, message=None):
        if datetime.strptime('1.4.{}'.format(datetime.utcnow().year), '%d.%m.%Y') == datetime.utcnow():
            await ctx.send("{} was reported to proper authorities!".format(ctx.author.nick or ctx.author.name))
        else:
            await ctx.send("This incident was reported to proper authorities!")
        if not isinstance(ctx.channel, discord.DMChannel):
            await ctx.message.delete()

    async def on_message(self, message: discord.Message):
        number = random.randint(1, 1000)

        if message.channel.name.__contains__('rp-'):
            return

        if message.content.lower().__contains__("hi bot"):
            emoji = self.bot.get_emoji(340954397502865409)
            if emoji:
                await message.add_reaction(emoji)

        if number > self.limit:
            if message.content.lower().__contains__("tharg") and number < 400:
                emoji = discord.utils.get(message.guild.emojis, name='tinfoilhat')
                await message.add_reaction(emoji or '👽')
                self.limit = default_chance

            if message.author.id == 186829544764866560 and message.content.lower().__contains__(
                    "by") and message.content.lower().__contains__("achenar") and number < 250:
                await message.add_reaction(random.choice(['🍺', '🍷', '🍸', '🍹', '🥃']))
                self.limit = default_chance

            if message.content.__contains__("Vigor"):
                emoji = discord.utils.get(message.guild.emojis, name='vigor')
                await message.add_reaction(emoji)
                self.limit = default_chance

            if message.content.__contains__("Sight"):
                emoji = discord.utils.get(message.guild.emojis, name='sight')
                await message.add_reaction(emoji)
                self.limit = default_chance

            if message.content.__contains__("Mind"):
                emoji = discord.utils.get(message.guild.emojis, name='mind')
                await message.add_reaction(emoji)
                self.limit = default_chance

            if message.content.__contains__("Aurora"):
                emoji = discord.utils.get(message.guild.emojis, name='aurora')
                await message.add_reaction(emoji)
                self.limit = default_chance

            if message.content.lower().__contains__("aisling") or message.content.lower().__contains__("duval"):
                emoji = discord.utils.get(message.guild.emojis, name='aislingduval')
                await message.add_reaction(emoji)
                self.limit = default_chance

            if message.content.lower().__contains__("kumo") or message.content.lower().__contains__("burger"):
                emoji = discord.utils.get(message.guild.emojis, name='KumoBurger')
                await message.add_reaction(emoji)
                self.limit = default_chance
        else:
            self.limit = self.limit - 10

        if isinstance(message.channel, discord.DMChannel):
            return
        

def setup(bot: commands.Bot):
    bot.add_cog(Fun(bot))

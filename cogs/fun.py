import discord
from discord.ext import commands
import random

default_chance = 600


class Fun:
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.limit = default_chance

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
        elif member.id == 186829544764866560:
            await ctx.send("BY ACHENAR... you compared to almighty Wisewolf? Please")
        elif member.id == 152527690291871745:
            await ctx.send("[REDACTED BY ADMINISTRATION - Clasified information]")
        else:
            await ctx.send("You will never be as awesome as Wisewolf")

    @commands.command()
    async def fix(self, ctx: commands.Context, message_id):
        return
        channel = ctx.guild.get_channel(338128432947003392)
        msg = await channel.get_message(int(message_id))

        for embed in msg.embeds:
            embed.set_thumbnail(url='https://media.discordapp.net/attachments/302178821405278208/342186320384491523/TheDailyChat.png?width=508&height=678')
            await msg.edit(embed=embed)

    async def on_message(self, message: discord.Message):
        number = random.randint(1, 1000)
        if message.author.id == 186829544764866560 and message.content.lower().__contains__("by achenar"):
            await message.add_reaction(random.choice(['🍺', '🍷', '🍸', '🍹', '🥃']))

        if message.content.lower().__contains__("hi bot"):
            emoji = self.bot.get_emoji(340954397502865409)
            if emoji:
                await message.add_reaction(emoji)

        if number > self.limit:
            if message.content.lower().__contains__("tharg"):
                emoji = discord.utils.get(message.guild.emojis, name='tinfoilhat')
                await message.add_reaction(emoji or '👽')
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
        else:
            self.limit = self.limit - 10


def setup(bot: commands.Bot):
    bot.add_cog(Fun(bot))

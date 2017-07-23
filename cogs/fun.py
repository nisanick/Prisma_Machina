import discord
from discord.ext import commands
import random


class Fun:
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def awesomenessof(self, ctx, who):
        options = [
            'Exceeding expectations',
            'Went down by 1 point since last time',
            'Needs to be 20% higher',
            '43',
            'Over safety limits',
            'Lesking from systems',
            'Hidden under the sofa'
        ]
        member = await commands.MemberConverter().convert(ctx, who)
        if member.id != 205504598792863744:
            await ctx.send("You will never be as awesome as Wisewolf")
        else:
            await ctx.send(random.choice(options))
        await ctx.message.delete("Command cleanup")

    @commands.Bot.event()
    async def on_message(self, message: discord.Message):
        print(message.content)
        if message.author.id == 186829544764866560 and message.content.lower().__contains__("by achenar"):
            await message.add_reaction('🍺')

        if message.content.lower().__contains__("thargoid"):
            print('here')
            emoji = discord.utils.get(message.guild.emojis, name='tinfoilhat')
            await message.add_reaction(emoji or '👽')


def setup(bot: commands.Bot):
    bot.add_cog(Fun(bot))

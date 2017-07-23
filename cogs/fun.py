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
        member = commands.MemberConverter().convert(ctx, who)
        if member.id != 205504598792863744:
            await ctx.send("You will never be as awesome as Wisewolf")
        else:
            await ctx.send(random.choice(options))
        await ctx.message.delete("Command cleanup")


def setup(bot: commands.Bot):
    bot.add_cog(Fun(bot))

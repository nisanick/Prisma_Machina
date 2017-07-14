from discord.ext import commands

class Greetings:
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def hi(self, ctx: commands.Context):
        who = ctx.message.author.mention
        await ctx.send("Greetings, {0}. I hope you have a nice day!".format(who))

    @commands.group()
    async def good(self):
        pass

    @good.command()
    async def night(self, ctx: commands.Context):
        await ctx.send("Good night {0}!".format(ctx.message.author.mention))
        await self.bot.logout()




def setup(bot: commands.Bot):
    bot.add_cog(Greetings(bot))

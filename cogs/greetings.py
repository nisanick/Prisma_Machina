from discord.ext import commands

class Greetings:
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def hi(self, ctx: commands.Context):
        who = ctx.message.author.mention
        await self.bot.say("hello, {0}. I hope you have a nice day!".format(who))




def setup(bot: commands.Bot):
    bot.add_cog(Greetings(bot))

from discord.ext import commands
import discord
import config
from datetime import datetime


class Testing:
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

    @commands.command()
    async def test(self, ctx: commands.Context):
        await ctx.send(ctx.message.author.discriminator)
        #print(" ".join(args[0:-1]))
        #print(args[-1])

    async def on_message(self, message):
        for word in message.content.split(" "):
            if not word.startswith("<"):
                for symbol in config.REPLACEMENTS:
                    word = word.replace(symbol, ' ')
        ''' what = message.content
        print('-- new message --')
        print('content: ' + what)
        what = what.split(" ")
        for word in what:
            # if word.__contains__()
            for c in word:
                print("{} code: {}".format(c, ord(c)))'''


def setup(bot: commands.Bot):
    bot.add_cog(Testing(bot))

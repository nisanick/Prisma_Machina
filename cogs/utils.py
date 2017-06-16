from discord.ext import commands
from datetime import datetime


class Utils:

    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def time(self):
        year = datetime.now().timetuple().tm_year
        now = datetime.utcnow().replace(year=(year + 1286)).strftime("%H:%M %d %b %Y")
        await self.bot.say(now)



def setup(bot):
    bot.add_cog(Utils(bot))
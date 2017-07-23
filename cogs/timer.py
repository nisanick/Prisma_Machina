

class Timer:
    def __init__(self, bot):
        self.bot = bot

    async def on_ready(self):
        await self.timer(1)
        pass


def setup(bot):
    bot.add_cog(Timer(bot))

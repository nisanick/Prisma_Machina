import discord

class Music:

    def __init__(self, bot):
        self.bot = bot
        discord.opus.load_opus()


def setup(bot):
    bot.add_cog(Music(bot))

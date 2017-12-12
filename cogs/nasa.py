from web import Web
import config
from discord.ext import commands
from datetime import datetime
import discord


class Nasa:
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def apod(self, ctx):
        """
        Shows Astronomical Picture of the Day straight from NASA
        """
        response = await Web.get_response("https://api.nasa.gov/planetary/apod?api_key={}".format(config.NASA_API))
        embed = discord.Embed(title='Astronomy Picture of the Day', description='**{}** | {}'.format(response["title"], response["date"]))
        embed.add_field(name='Explanation', value=response['explanation'][0, 2000], inline=False)
        embed.add_field(name='HD Download', value='[Click here!]({})'.format(response["hdurl"]))
        embed.set_image(url=response['url'])
        embed.timestamp = datetime.utcnow()
        embed.set_footer(text='Generated on ')

        await ctx.send(content=None, embed=embed)
        await ctx.message.delete()


def setup(bot: commands.Bot):
    bot.add_cog(Nasa(bot))

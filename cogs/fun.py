# coding=utf-8
import discord
from discord.ext import commands
import random
from web import Web
from data.links import donation_link
import database
import config
from datetime import datetime
import asyncio

default_chance = 600


class Fun:
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.limit = default_chance
        self.duck_message = None
        self.duck_shots = 0
        self.users = []
        self.last_duck = 0

    @commands.command()
    async def awesomenessof(self, ctx, who):
        """
        Tells you how awesome you are in comparison to Wisewolf.
        """
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
        elif member.id == 186829544764866560:  # Techeron
            await ctx.send("BY ACHENAR... you compared to almighty Wisewolf? Please")
        elif member.id == 351706853153046549:  # Ryan
            await ctx.send("[REDACTED BY ADMINISTRATION - Classified information]")
        elif member.id == 360543179591909397:  # Bear
            await ctx.send("Rupey is as awesome as a teacher can be.")
        else:
            if datetime.strptime('1.4.{}'.format(datetime.utcnow().year), '%d.%m.%Y') == datetime.utcnow():
                await ctx.send("Everyone is better than Wisewolf")
            else:
                await ctx.send("You will never be as awesome as Wisewolf")

    @commands.command(hidden=True)
    async def report(self, ctx, *, message=None):
        if datetime.strptime('1.4.{}'.format(datetime.utcnow().year), '%d.%m.%Y') == datetime.utcnow():
            await ctx.send("{} was reported to proper authorities!".format(ctx.author.nick or ctx.author.name))
        else:
            await ctx.send("This incident was reported to proper authorities!")
        if not isinstance(ctx.channel, discord.DMChannel):
            await ctx.message.delete()

    @commands.command(name='sudoku', aliases=['cs', 'commitsudoku'])
    async def _sudoku(self, ctx):
        embed = discord.Embed(title='Argh')
        embed.set_image(url='http://nisanick.com/pictures/{}'.format('sudoku.png'))
        embed.timestamp = datetime.utcnow()
        embed.set_footer(text='Generated on ')
        await ctx.send(content=None, embed=embed)
        await ctx.message.delete()

    async def on_message(self, message: discord.Message):
        number = random.randint(1, 1000)

        if message.channel.name.__contains__('rp-'):
            return

        if message.content.lower().__contains__("hi bot"):
            emoji = self.bot.get_emoji(340954397502865409)
            if emoji:
                await message.add_reaction(emoji)

        if number > self.limit:
            if message.content.lower().__contains__("tharg") and number < 400:
                emoji = discord.utils.get(message.guild.emojis, name='tinfoilhat')
                await message.add_reaction(emoji or '👽')
                self.limit = default_chance

            if message.author.id == 186829544764866560 and message.content.lower().__contains__(
                    "by") and message.content.lower().__contains__("achenar") and number < 250:
                await message.add_reaction(random.choice(['🍺', '🍷', '🍸', '🍹', '🥃']))
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

            if message.content.lower().__contains__("kumo") or message.content.lower().__contains__("burger"):
                emoji = discord.utils.get(message.guild.emojis, name='KumoBurger')
                await message.add_reaction(emoji)
                self.limit = default_chance
        else:
            self.limit = self.limit - 10

        if isinstance(message.channel, discord.DMChannel):
            return

        if number > 700 and datetime.strptime('24.12.{}'.format(datetime.utcnow().year),
                                              '%d.%m.%Y') < datetime.utcnow() < datetime.strptime(
                '27.12.{}'.format(datetime.utcnow().year), '%d.%m.%Y'):
            await message.add_reaction(random.choice(['⛄', '❄️', '🌟', '🍪', '🎅', '🤶', '🎄', '🔔', '🎶']))

        if self.last_duck > 500 or (self.last_duck > 30 and random.randint(1, 1000) > 985):
            if message.content.startswith(tuple(config.PREFIX)):
                return
            self.duck_message = message
            self.duck_shots = 0
            self.users = [294171600478142466]
            self.last_duck = 0
            reaction = '🦆'
            if datetime.strptime('24.12.{}'.format(datetime.utcnow().year),
                                 '%d.%m.%Y') < datetime.utcnow() < datetime.strptime(
                    '27.12.{}'.format(datetime.utcnow().year), '%d.%m.%Y'):
                reaction = '🎁'
            elif datetime.strptime('1.4.{}'.format(datetime.utcnow().year), '%d.%m.%Y') == datetime.utcnow():
                reaction = '🔫'

            await asyncio.sleep(random.randint(1, 60))
            await self.duck_message.add_reaction(reaction)
        else:
            self.last_duck += 1

    async def on_reaction_add(self, reaction, user):
        if self.duck_message is None:
            return
        if user.id in self.users:
            return
        hunt = '🔫'
        if datetime.strptime('24.12.{}'.format(datetime.utcnow().year),
                             '%d.%m.%Y') < datetime.utcnow() < datetime.strptime(
                '27.12.{}'.format(datetime.utcnow().year), '%d.%m.%Y'):
            hunt = '🎁'
        elif datetime.strptime('1.4.{}'.format(datetime.utcnow().year), '%d.%m.%Y') == datetime.utcnow():
            hunt = '🦆'
        if reaction.emoji == hunt and reaction.message == self.duck_message:
            self.users.append(user.id)
            self.duck_shots += 1
            amount = 1
            if self.duck_shots == 1:
                amount = 6

            # if self.duck_message.created_at.timestamp() + 15 > datetime.utcnow().timestamp():
            #    amount += 4
            values = {
                'giver': 294171600478142466,
                'receiver': user.id,
                'amount': amount
            }

            await Web.get_response(donation_link, values)

            insert = "INSERT INTO users (user_id, message_count, reaction_count, special, ducks) VALUES ($1, 0, 0, 0, 1) ON CONFLICT (user_id) DO UPDATE SET ducks = users.ducks + 1"
            db = await database.Database.get_connection(self.bot.loop)
            async with db.transaction():
                await db.execute(insert, str(user.id))
            await database.Database.close_connection(db)

    @commands.command(hidden=True)
    async def wuwhu(self, ctx):
        await ctx.message.delete()
        await ctx.send(file=discord.File('{}img/tech_wuwhu.PNG'.format(config.BASE_DIR)))

def setup(bot: commands.Bot):
    bot.add_cog(Fun(bot))

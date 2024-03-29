import asyncio
import random
from datetime import datetime
from datetime import timedelta

import discord
from discord.ext import commands

import checks
import database
from paginator import HelpPaginator, CannotPaginate
import config
from web import Web
from data.links import *


class Utils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='roll')
    async def _roll(self, ctx, *, roll_string: str):
        """
        Rolls a dice specified in roll_string. Use `?help roll` for more information.
        
        Parameter roll_string supports following:
        - constant integer number, for example `?roll 4` to get specific result
        - symbol 'd' followed by a positive integer number x to generate number in range 1 to x, inclusive, for example `?roll d20`
        - symbol '+' or '-' to add or subtract more numbers together, for example `?roll d20+4`
        - symbol '<' or '>' to check if left side is lower or higher than right side of equation, for example `?roll d20+4 > 10`
        
        Some aditional things to keep in mind:
        - roll_string can contain at most one '<' or '>'
        - both constant and generated numbers can be used on both sides of equation
        - both '+' and '-' can be used on both sides of equation multiple times
        - both constant and generated number can be used on both sides of '+' and '-'
        """
        left = roll_string.strip(" ")
        right = None
        mod = None

        if roll_string.__contains__('<'):
            left = roll_string.split('<')[0].strip(" ")
            right = roll_string.split('<')[1].strip(" ")
            mod = '<'
        elif roll_string.__contains__('>'):
            left = roll_string.split('>')[0].strip(" ")
            right = roll_string.split('>')[1].strip(" ")
            mod = '>'

        total = 0
        result = ''
        first = True
        for add_rolls in left.split('+'):
            sub_total = 0
            iterations = -1
            for sub in add_rolls.split('-'):
                iterations += 1
                if sub.lower().__contains__('d'):
                    if sub.startswith('d'):
                        dices = 1
                        sides = sub.split('d')[1]
                    else:
                        dices = sub.split('d')[0]
                        sides = sub.split('d')[1]

                    rolled = 0
                    for i in range(0, int(dices)):
                        if not first:
                            result += ', '
                        first = False
                        temp = random.randint(1, int(sides))
                        result += str(temp)
                        rolled += temp
                elif self.is_number(sub):
                    rolled = int(sub)
                    if not first:
                        result += ', '
                    first = False
                    result += str(rolled)
                if iterations == 0:
                    sub_total += rolled
                else:
                    sub_total -= rolled
            total += sub_total

        if not result.__contains__(','):
            result = ''
        else:
            result = '[{}]'.format(result)

        embed = discord.Embed(title='Roll {}'.format(roll_string), description="{} \n{}".format(total, result), color=discord.Color.orange())
        embed.set_author(name=ctx.message.author.nick or ctx.message.author.display_name, icon_url=ctx.message.author.avatar_url)
        if mod is None:
            await ctx.send('', embed=embed)
            if not isinstance(ctx.channel, discord.DMChannel):
                await ctx.message.delete()
        else:
            if mod is '<':
                diff = total < int(right)
            else:
                diff = total > int(right)

            if diff:
                embed.description = 'Pass ({}) \n{}'.format(total, result)
                embed.colour = discord.Color.green()
            else:
                embed.description = 'Fail ({}) \n{}'.format(total, result)
                embed.colour = discord.Color.red()

            await ctx.send('', embed=embed)
            if not isinstance(ctx.channel, discord.DMChannel):
                await ctx.message.delete()

    def is_number(self, tested):
        try:
            int(tested)
            return True
        except ValueError:
            return False

    @commands.command(name='help')
    async def _help(self, ctx, *, command: str = None):
        """Shows this message. If you supply a 'command' parameter, help for that command or group of commands will be given instead."""
        if not isinstance(ctx.channel, discord.DMChannel):
            await ctx.message.delete()
        try:
            if command is None:
                p = await HelpPaginator.from_bot(ctx)
            else:
                entity = self.bot.get_cog(command) or self.bot.get_command(command)

                if entity is None:
                    return await ctx.send('Command "{}" not found.'.format(command))
                elif isinstance(entity, commands.Command):
                    p = await HelpPaginator.from_command(ctx, entity)
                else:
                    p = await HelpPaginator.from_cog(ctx, entity)

            await p.paginate()
        except CannotPaginate as e:
            await ctx.send(e)

    @commands.command()
    async def feedback(self, ctx, *, message):
        """Sends your feedback to High Council."""
        embed = discord.Embed(title="Feedback", description=message, colour=discord.Colour.green(), timestamp=datetime.utcnow())
        embed.set_author(name=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
        for channel_id in config.ADMINISTRATION_CHANNELS:
            await ctx.bot.get_channel(channel_id).send("", embed=embed)
        await ctx.message.add_reaction('✅')

    @commands.command()
    async def link(self, ctx, verification, *, account):
        """Links your discord and web account together. This allows more bot features for you."""
        link = account_link
        args = {
            'discord_id': ctx.message.author.id,
            'username': account,
            'verification': verification,
            'discord_name': "{}#{}".format(ctx.message.author.name, ctx.message.author.discriminator)
        }
        response = await Web.get_response(link, args)
        to_delete = [ctx.message]
        if response['Response'] == 'User not found':
            to_delete.append(
                await ctx.send(
                    '❌ Please register on our website first\nhttp://www.prismatic-imperium.com/reg_form.php'))
        elif response['Response'] == 'Invalid Verification Code':
            to_delete.append(
                await ctx.send('❌ Check your verification code and try again.'))
        elif response['Response'] == 'Success':
            to_delete.append(
                await ctx.send('✅'))
        elif response['Response'] == 'Account is already linked':
            to_delete.append(
                await ctx.send('❌ This account is already linked to Discord.'))
        await asyncio.sleep(5)
        if not isinstance(ctx.channel, discord.DMChannel):
            await ctx.channel.delete_messages(to_delete)

    @commands.command()
    async def time(self, ctx):
        """Shows current Galactic Time."""
        year = datetime.utcnow().timetuple().tm_year
        now = datetime.utcnow().replace(year=(year + 1286)).strftime("%H:%M %d %b %Y")
        embed = discord.Embed(title="Current Galactic Time", description=now, color=discord.Colour.dark_orange())
        if not isinstance(ctx.channel, discord.DMChannel):
            await ctx.message.delete()
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        try:
            if member.display_name.__contains__('💎'):
                return
            if member.guild.id != 205356098293727233:
                return
        except Exception:
            print("nope")
        channel = self.bot.get_channel(int(config.ANNOUNCE_CHANNEL))
        mention = ""
        for role in member.guild.roles:
            if role.name == 'High Council':
                mention = role.mention
        await self.bot.get_channel(int(config.ADMINISTRATION_CHANNEL)).send(
            "{} just joined the server. {}".format(member.mention, mention))
        await asyncio.sleep(5)
        await channel.send(config.WELCOME.format(member.mention))

    @commands.command(hidden=True)
    @commands.check(checks.can_manage_bot)
    async def probe(self, ctx, *, who):
        user = await commands.MemberConverter().convert(ctx, who)
        if user.id == 163037317278203908:
            await ctx.send("I can't figure out where the probe should go.")
            return
        probation = discord.utils.find(lambda r: r.name == 'Probation', ctx.guild.roles)
        senator = discord.utils.find(lambda r: r.name == 'Senator', ctx.guild.roles)
        await user.add_roles(*[probation, senator])
        insert_probation = "INSERT INTO schedule(event_time, event_type, event_special) VALUES ($1, 1, $2)"
        time = datetime.utcnow() + timedelta(days=14)
        values = [
            time,
            str(user.id)
        ]
        db = await database.Database.get_connection(self.bot.loop)
        async with db.transaction():
            await db.execute(insert_probation, *values)
            await ctx.send("Probation for {} should end at {:%d.%m.%Y %H:%M} (UTC)".format(user.mention, time))
            await ctx.message.delete()
        await database.Database.close_connection(db)

    @commands.command(name='schedule')
    @commands.check(checks.can_manage_bot)
    async def _schedule(self, ctx):
        """
        *Admin only* | Information about all scheduled events, like probation or news check.
        """
        if not isinstance(ctx.channel, discord.DMChannel):
            await ctx.message.delete()
        event_select = "SELECT event_id, event_type, event_special, event_time FROM schedule WHERE done = FALSE"

        db = await database.Database.get_connection(self.bot.loop)
        async with db.transaction():
            embed = discord.Embed(colour=discord.Colour(0xFFF91A), title='Schedule info', description="Currently scheduled events:")
            embed.timestamp = datetime.utcnow()
            embed.set_footer(text="Generated at")
            async for (event_id, event_type, event_special, event_time) in db.cursor(event_select):

                # Website article
                if event_type == 0:
                    embed.add_field(name="News check", value="{:%d.%m.%Y %H:%M}\nLast id: {}".format(event_time, event_special))

                # Probation
                if event_type == 1:
                    member = ctx.guild.get_member(int(event_special))
                    embed.add_field(name="Probation expire", value="{:%d.%m.%Y %H:%M}\n{}".format(event_time, member.mention))

                # RP message
                elif event_type == 2:
                    pass
                    # await self.send_article(int(event_special), True)

                # APOD
                elif event_type == 3:
                    embed.add_field(name="APOD article check", value="{:%d.%m.%Y %H:%M}\nLast article: {}".format(event_time, event_special))
            await ctx.send(embed=embed)
        await database.Database.close_connection(db)


    @commands.Cog.listener()
    async def on_member_remove(self, member):
        channel = self.bot.get_channel(int(config.ADMINISTRATION_CHANNEL))
        if isinstance(member, discord.Member):
            await channel.send('{} left the server. {}'.format(member.name, member.mention))
        else:
            await channel.send('{} left the server'.format(member.name))


    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.id == self.bot.user.id or message.content.startswith(tuple(config.PREFIX)):
            return
        if isinstance(message.channel, discord.DMChannel):

            embed = discord.Embed(title="DM to bot", description=message.content, colour=discord.Colour.blurple(),
                                  timestamp=message.created_at.utcnow())
            embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)
            channel = self.bot.get_channel(int(config.ADMINISTRATION_CHANNEL))
            await channel.send("", embed=embed)
            await message.add_reaction('✅')

    @commands.Cog.listener()
    async def on_user_update(self, before: discord.User, after: discord.User):
        if before.name != after.name or before.discriminator != after.discriminator:
            link = update_link
            args = {
                'discord_id': after.id,
                'key': config.TRANSACTION_KEY,
                'discord_name': "{}#{}".format(after.name, after.discriminator)
            }
            response = await Web.get_response(link, args)

    @commands.command(name='rescan_names', hidden=True)
    @commands.check(checks.can_manage_bot)
    @commands.check(checks.in_admin_channel)
    async def _update_all_discord_names(self, ctx):
        async with ctx.typing():
            errors = []
            async for member in ctx.guild.fetch_members(limit=None):
                link = update_link
                args = {
                    'discord_id'  : member.id,
                    'key'         : config.TRANSACTION_KEY,
                    'discord_name': "{}#{}".format(member.name, member.discriminator)
                }
                response = await Web.get_response(link, args)
                print(response)
                if response['Code'] == 0 or response['Code'] == 1:
                    pass
                else:
                    errors.append(member.name)
            print(",".join(errors))
            

def setup(bot):
    bot.add_cog(Utils(bot))


import asyncio
import random
from datetime import datetime

import discord
from discord.ext import commands

import checks
import database
from paginator import HelpPaginator, CannotPaginate
import config
from web import Web
from data.links import *


class Utils:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='help')
    async def _help(self, ctx, *, command: str = None):
        # return
        """Shows help about a command or the bot"""
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
        """Sends your feedback to High Council"""
        embed = discord.Embed(title="Feedback", description=message, colour=discord.Colour.green(), timestamp=datetime.utcnow())
        embed.set_author(name=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
        channel = await commands.TextChannelConverter().convert(ctx, config.ADMINISTRATION_CHANNEL)
        # channel = await commands.TextChannelConverter().convert(ctx, '210467116392906753')
        await channel.send("<@163037317278203908>", embed=embed)
        # await channel.send("", embed=embed)
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
        """Shows current Galactic Time"""
        year = datetime.now().timetuple().tm_year
        now = datetime.utcnow().replace(year=(year + 1286)).strftime("%H:%M %d %b %Y")
        embed = discord.Embed(title="Current Galactic Time", description=now, color=discord.Colour.dark_orange())
        if not isinstance(ctx.channel, discord.DMChannel):
            await ctx.message.delete()
        await ctx.send(embed=embed)

    async def on_member_join(self, member: discord.Member):
        channel = self.bot.get_channel(int(config.ANNOUNCE_CHANNEL))
        await channel.send(config.WELCOME.format(member.mention))
        mention = ""
        for role in member.guild.roles:
            if role.name == 'Council Member':
                mention = role.mention
        await self.bot.get_channel(int(config.ADMINISTRATION_CHANNEL)).send(
            "{} just joined the server. {}".format(member.mention, mention))

    @commands.command(hidden=True)
    @commands.check(checks.can_manage_bot)
    async def probe(self, ctx, *, who):
        user = await commands.MemberConverter().convert(ctx, who)
        probation = discord.utils.find(lambda r: r.name == 'Probation', ctx.guild.roles)
        senator = discord.utils.find(lambda r: r.name == 'Senator', ctx.guild.roles)
        await user.add_roles(*[probation, senator])
        insert_probation = "INSERT INTO schedule(event_time, event_type, event_special) VALUES ($1, 1, $2)"
        time = datetime.fromtimestamp(datetime.utcnow().timestamp() + 1209600)
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

    async def on_member_remove(self, member):
        channel = self.bot.get_channel(int(config.ADMINISTRATION_CHANNEL))
        if isinstance(member, discord.Member):
            await channel.send('{} left the server. {}'.format(member.name, member.mention))
        else:
            await channel.send('{} left the server'.format(member.name))

    @commands.command(name='say')
    @commands.check(checks.can_manage_bot)
    @commands.check(checks.in_say_channel)
    async def _say(self, ctx, channel: discord.TextChannel, *, message):
        await channel.send(message)

    @commands.command(name='dm')
    @commands.check(checks.can_manage_bot)
    @commands.check(checks.in_say_channel)
    async def _dm(self, ctx, user: discord.User, *, message):
        channel = user.dm_channel
        if channel is None:
            await user.create_dm
            channel = user.dm_channel
        await channel.send(message)

    @commands.command(name='embed', hidden=True)
    @commands.check(checks.can_manage_bot)
    @commands.check(checks.in_admin_channel)
    async def _embed(self, ctx, channel: discord.TextChannel):
        pass


def setup(bot):
    bot.add_cog(Utils(bot))

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
        await ctx.message.delete(reason="Command cleanup.")
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
        embed = discord.Embed(title="Suggestion", description=message, colour=discord.Colour.green(), timestamp=datetime.utcnow())
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
            await ctx.channel.delete_messages(to_delete, reason="Command and response cleanup.")

    @commands.command()
    async def time(self, ctx):
        """Shows current Galactic Time"""
        year = datetime.now().timetuple().tm_year
        now = datetime.utcnow().replace(year=(year + 1286)).strftime("%H:%M %d %b %Y")
        embed = discord.Embed(title="Current Galactic Time", description=now, color=discord.Colour.dark_orange())
        if not isinstance(ctx.channel, discord.DMChannel):
            await ctx.message.delete(reason="Command cleanup")
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

    async def on_member_remove(self, member):
        channel = self.bot.get_channel(int(config.ADMINISTRATION_CHANNEL))
        if isinstance(member, discord.Member):
            await channel.send('{} left the server. {}'.format(member.name, member.mention))
        else:
            await channel.send('{} left the server'.format(member.name))


def setup(bot):
    bot.add_cog(Utils(bot))

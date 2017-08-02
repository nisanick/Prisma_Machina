# /bin/python3
from datetime import datetime

import discord
from discord.ext import commands
import database
import asyncio

import config
import checks
# from importlib import reload as rld
import logging

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

bot = commands.Bot(command_prefix=config.PREFIX, help_attrs=config.HELP_ATTRIBUTES, game=discord.Game(name='services to CMDRs'))

startup = datetime.utcnow()


@bot.event
async def on_ready():
    await database.Database.init_connection(bot.loop)
    print("Client logged in")
    print(startup)
    print(bot.user.name)
    print(bot.user.id)


@bot.command(hidden=True)
@commands.check(checks.can_manage_bot)
@commands.check(checks.in_admin_channel)
async def load(ctx, *args):
    if ctx.author.id not in config.ADMIN_USERS:
        return
    if args.__len__() <= 0:
        to_delete = await ctx.send("No argument passed")
        await asyncio.sleep(5)
        await to_delete.delete()
        return
    what = 'cogs.{0}'.format(args[0])
    if not what in config.EXTENSIONS:
        config.EXTENSIONS.append(what)
    bot.load_extension(what)
    await ctx.send("Extension {0} loaded".format(what))


@bot.command(hidden=True)
@commands.check(checks.can_manage_bot)
@commands.check(checks.in_admin_channel)
async def unload(ctx: commands.Context, *args):
    if ctx.author.id not in config.ADMIN_USERS:
        return
    if args.__len__() <= 0:
        await ctx.send("No argument passed")
        return
    what = 'cogs.{0}'.format(args[0])
    if what == 'cogs.permisions':
        await ctx.send("Permisions can't be unloaded")
        return
    if what in config.EXTENSIONS:
        config.EXTENSIONS.remove(what)
        bot.unload_extension(what)
        await ctx.send("Extension {0} uloaded".format(what))
    else:
        await ctx.send("Extension {0} wasn't loaded".format(what))


@bot.command(hidden=True)
@commands.check(checks.can_manage_bot)
@commands.check(checks.in_admin_channel)
async def reload(ctx, *args):
    if args.__len__() <= 0:
        await ctx.send("No argument passed")
        return
    if args[0] == 'all':
        to_reload = config.EXTENSIONS
    else:
        to_reload = ["cogs.{0}".format(args[0])]
    for extension in to_reload:
        if extension in config.EXTENSIONS:
            await ctx.send('reloading {}'.format(extension))
            bot.unload_extension(extension)
            bot.load_extension(extension)


@bot.event
async def on_command_error(ctx, error):
    to_delete = [ctx.message]
    if ctx.guild is not None:
        permissions = ctx.channel.permissions_for(ctx.guild.me)
    else:
        permissions = ctx.channel.permissions_for(ctx.bot.user)
    if permissions.send_messages:
        to_delete.append(
            await ctx.send('❌ We are sorry, your command was not recognized. Please refer to the Help command. ❌'))
    if isinstance(error, commands.MissingRequiredArgument):
        print("argument missing")
    else:
        channel = await commands.TextChannelConverter().convert(ctx, config.ADMINISTRATION_CHANNEL)
        embed = discord.Embed(title="Command invocation error.", description=str(error), color=discord.Colour.red())
        embed.add_field(name="User", value=ctx.message.author.mention)
        if isinstance(ctx.channel, discord.DMChannel):
            ch = ctx.channel.recipient.mention
        elif isinstance(ctx.channel, discord.TextChannel):
            ch = ctx.channel.mention
        else:
            ch = ctx.channel.name
        embed.add_field(name="Channel", value=ch)
        embed.add_field(name="Command", value=ctx.invoked_with)
        embed.add_field(name="Time", value="{:%d.%m.%Y %H:%M} (UTC)".format(datetime.utcnow()))
        await channel.send("<@163037317278203908>", embed=embed)
    await asyncio.sleep(5)
    if not isinstance(ctx.channel, discord.DMChannel):
        await ctx.channel.delete_messages(to_delete, reason="Command cleanup")


bot.remove_command('help')
for ext in config.EXTENSIONS:
    bot.load_extension(ext)
bot.run(config.TOKEN, reconnect=True)

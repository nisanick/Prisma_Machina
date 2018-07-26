# /bin/python3
from datetime import datetime

import discord
from discord.ext import commands
import database
import asyncio

import sys
import os
import config
import checks
# from importlib import reload as rld
import logging

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

bot = commands.Bot(command_prefix=config.PREFIX, help_attrs=config.HELP_ATTRIBUTES, activity=discord.Activity(name='services to CMDRs', type=discord.ActivityType.playing), case_insensitive=True)

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
    if what not in config.EXTENSIONS:
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


bot.remove_command('help')
for ext in config.EXTENSIONS:
    bot.load_extension(ext)
bot.run(config.TOKEN, reconnect=True)
os.execv(sys.executable, ['python'] + sys.argv)
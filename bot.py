# /bin/python3
from datetime import datetime

import discord
from discord.ext import commands
from discord.ext.commands import ExtensionAlreadyLoaded

import database
import asyncio
import socketio
from dateutil.parser import isoparse

import config
import checks
import logging
from eddn import eddn

intents = discord.Intents.default()
intents.members = True

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

bot = commands.Bot(command_prefix=config.PREFIX, help_attrs=config.HELP_ATTRIBUTES, activity=discord.Activity(name='services to CMDRs', type=discord.ActivityType.playing), case_insensitive=True, intents=intents)

startup = datetime.utcnow()


@bot.event
async def on_ready():
    await database.Database.init_connection(bot.loop)
    print("Client logged in")
    print(startup)
    print(bot.user.name)
    print(bot.user.id)
    bgs = bot.get_cog('BGS')
    if bgs is None:
        bot.load_extension('cogs.bgs')
    await bot.get_cog('BGS').init_bgs()
    await asyncio.gather(eddn(bot), ticker())


@bot.command()
@commands.check(checks.can_manage_bot)
@commands.check(checks.in_admin_channel)
async def load(ctx, *module):
    """*Admin only* | *Admin channel only* | Loads a module from disk.
        This command serves to load a set of commands from disk without restarting the whole bot. Can be used to allow certain commands to be used again or load a new set of commands.
        Module name can be derived from the help page name.
        !!Please don't use this command unless there is no other option. Restarting the bot or contacting Nisanick#5824 are prefered options!!
         """
    if ctx.author.id not in config.ADMIN_USERS:
        return

    if module.__len__() <= 0:
        to_delete = await ctx.send("No argument passed")
        await asyncio.sleep(5)
        await to_delete.delete()
        return

    what = 'cogs.{0}'.format(module[0])
    if what not in config.EXTENSIONS:
        config.EXTENSIONS.append(what)
    try:
        bot.load_extension(what)
        await ctx.send("Extension {0} loaded".format(what))
    except ExtensionAlreadyLoaded as error:
        await ctx.send("Extension {0} already loaded".format(what))


@bot.command()
@commands.check(checks.can_manage_bot)
@commands.check(checks.in_admin_channel)
async def unload(ctx: commands.Context, *args):
    """*Admin only* | *Admin channel only* | Removes a module from bot.
        This command serves to remove a set of commands from the bot without the need to restart it. Can be used to prevent certain commands to be used.
        Module name can be derived from the help page name.
        !!Please don't use this command unless there is no other option. Restarting the bot or contacting Nisanick#5824 are prefered options!!
         """
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


@bot.command()
@commands.check(checks.can_manage_bot)
@commands.check(checks.in_admin_channel)
async def reload(ctx, *args):
    """*Admin only* | *Admin channel only* | Reloads a module from disk.
        This command serves to reload a set of commands from disk without without restarting the whole bot. Effect is the same as using unload and then load command.
        Module name can be derived from the help page name. If 'all' is sent instead of a specific module, all modules are reloaded.
        !!Please don't use this command unless there is no other option. Restarting the bot or contacting Nisanick#5824 are prefered options!!
         """
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


sio = socketio.AsyncClient()
bot.bgs_run = True


@sio.event
async def connect():
    print('connection established')


@sio.event
async def message(data):
    print('message received with ', data)
    await update_tick(data)


@sio.event
async def tick(data):
    print('new tick detected @ ', data)
    await update_tick(data)


@sio.event
async def disconnect():
    print('disconnected from server')


async def ticker():
    while bot.bgs_run:
        try:
            await sio.connect('http://tick.phelbore.com:31173')
            await sio.wait()
        except socketio.exceptions.ConnectionError as e:
            print(e)
            await asyncio.sleep(5)
    
    
async def update_tick(data):
    date = isoparse(data)
    bgs = bot.get_cog('BGS')
    if bgs is None:
        bot.load_extension('cogs.bgs')
        bgs = bot.get_cog('BGS')
    await bgs.set_tick_date(date)


@bot.command(name="restart")
@commands.check(checks.can_manage_bot)
@commands.check(checks.in_admin_channel)
async def _restart(ctx):
    """*Admin only* | *Admin channel only* | Mericful shutdown and restart of the bot.
        Closes all IO operations and disconnects the bot from discord, practically stoping the script. System then restarts the bot again.
        !!This is a prefered option to deal with restarts if they are needed. Please don't unload/load modules on your own!!
         """
    await ctx.message.add_reaction('✅')
    bot.bgs_run = False
    await sio.disconnect()
    await bot.close()
    bot.loop.close()

bot.remove_command('help')
for ext in config.EXTENSIONS:
    bot.load_extension(ext)
try:
    bot.run(config.TOKEN, reconnect=True)
except Exception as e:
    print(e)
print("restart")

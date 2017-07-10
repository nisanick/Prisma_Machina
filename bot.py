#/bin/python3
import asyncio
import discord
from discord import Client
from discord.ext import commands
from config import *
from importlib import reload as rld
import sched, time
from datetime import datetime

# prisma = discord.Client()
bot = commands.Bot(command_prefix=PREFIX, description=DESCRIPTION, help_attrs=HELP_ATTRIBUTES)

extensions = [
    'cogs.utils',
    'cogs.parsing'
]
shcedule = sched.scheduler(time.time, time.sleep)

server = None

@bot.event
async def on_ready():
    print("Client logged in")
    print(bot.user.name)
    print(bot.user.id)
    await bot.change_presence(game=discord.Game(name="with your heart"))





@bot.command(pass_context=True)
async def hello(ctx, *args):
    print(bot.get_server(295572327826194434).__class__)


@bot.command(pass_context=True)
async def load(ctx, *args):
    if ctx.message.author.id not in ADMIN_USERS:
        return
    if args.__len__() <= 0:
        await bot.say("No argument passed")
        return
    what = 'cogs.{0}'.format(args[0])
    if not what in extensions:
        extensions.append(what)
    bot.load_extension(what)
    await bot.say("Extension {0} loaded".format(what))


@bot.command(pass_context=True)
async def unload(ctx: commands.Context, *args):
    if ctx.message.author.id not in ADMIN_USERS:
        return
    if args.__len__() <= 0:
        await bot.say("No argument passed")
        return
    what = 'cogs.{0}'.format(args[0])
    if what == 'cogs.permisions':
        await bot.say("Permisions can't be unloaded")
        return
    if what in extensions:
        extensions.remove(what)
        bot.unload_extension(what)
        await bot.say("Extension {0} uloaded".format(what))
    else:
        await bot.say("Extension {0} wasn't loaded".format(what))


@bot.command(pass_context=True)
async def reload(ctx, *args):
    if ctx.message.author.id not in ADMIN_USERS:
        return
    if args.__len__() <= 0:
        await bot.say("No argument passed")
        return
    print(args)
    if args[0] == 'all':
        to_reload = extensions
    else:
        to_reload = ["cogs.{0}".format(args[0])]
    for extension in to_reload:
        print(extension)
        if extension in extensions:
            print('reloading')
            bot.unload_extension(extension)
            bot.load_extension(extension)


@bot.event
async def on_message(message):
    await bot.process_commands(message)


for ext in extensions:
    bot.load_extension(ext)
bot.remove_command('help')
bot.run(TOKEN)

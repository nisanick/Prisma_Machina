#/bin/python3
import discord
from discord import Client
from discord.ext import commands
from config import *

# prisma = discord.Client()
bot = commands.Bot(command_prefix='!')

extensions = [
    'cogs.utils',
    'cogs.parsing'
]

@bot.event
async def on_ready():
    print("Client logged in")
    print(bot.user.name)
    print(bot.user.id)
    await bot.change_presence(game=discord.Game(name="with your heart"))


@bot.command()
async def hello(*args):
    return await bot.say("!hello")


@bot.command()
async def load(*args):
    if args.__len__() <= 0:
        await bot.say("No argument passed")
        return
    what = 'cogs.{0}'.format(args[0])
    if what in extensions:
        bot.load_extension(what)
        await bot.say("Extension {0} loaded".format(what))
    else:
        await bot.say("No such extension available")


@bot.command()
async def register(*args):
    if args.__len__() <= 0:
        await bot.say("No argument passed")
        return
    what = 'cogs.{0}'.format(args[0])
    extensions.append(what)
    await bot.say("Extension {0} registered".format(what))


@bot.command()
async def reload(*args):
    if args.__len__() <= 0:
        await bot.say("No argument passed")
        return
    print(args)
    if args[0] == 'all':
        to_reload = extensions
    else:
        to_reload = []
        to_reload.append("cogs.{0}".format(args[0]))
    for extension in to_reload:
        print(extension)
        if extension in extensions:
            print('reloading')
            bot.unload_extension(extension)
            bot.load_extension(extension)


@bot.event
async def on_message(message):
    words = message.content.split(" ")
    await bot.process_commands(message)


for ext in extensions:
    bot.load_extension(ext)
bot.run(TOKEN)

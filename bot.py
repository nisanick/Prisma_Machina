import discord
from discord import Client
from discord.ext import commands

# prisma = discord.Client()
bot = commands.Bot(command_prefix='!')

extensions = [
    'cogs.utils'
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
    await bot.say(what)
    if what in extensions:
        bot.load_extension(what)
    else:
        await bot.say("No such extension available")


@bot.command()
async def register(*args):
    if args.__len__() <= 0:
        await bot.say("No argument passed")
        return
    what = 'cogs.{0}'.format(args[0])
    extensions.append(what)
    await bot.say("Extension registered")


@bot.command()
async def reload(*args):
    if args.__len__() <= 0:
        await bot.say("No argument passed")
        return
    print(args)
    if args[0] == 'all':
        ext = extensions
    else:
        ext = args
    for e in ext:
        if e in extensions:
            bot.unload_extension(e)
            bot.load_extension(e)


@bot.event
async def on_message(message):
    # TODO - parse messages and save most used words to database
    await bot.process_commands(message)


bot.run("""{token}""")

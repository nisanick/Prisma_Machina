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
startup = datetime.utcnow()

@bot.event
async def on_ready():
    print("Client logged in")
    print(bot.user.name)
    print(bot.user.id)
    startup = datetime.utcnow()
    await bot.change_presence(game=discord.Game(name="with your heart"))


@bot.command(pass_context=True)
async def hello(ctx: commands.Context, *args):
    #print(bot.get_server(295572327826194434).__class__)
    #channel = commands.ChannelConverter(ctx, '322456259897065472').convert()
    #print(channel.name)
    channel = commands.ChannelConverter(ctx, args[0]).convert()
    limit = args[1]
    users = dict()
    limit = int(limit)
    count = limit
    before = startup
    bot.type()
    while count == limit:
        count = 0
        async for message in bot.logs_from(channel, limit=int(limit), before=before):
            who = message.author.id
            users[who] = users.get(who, 0) + 1
            count = count + 1
            before = message

    for user in users.keys():
        name = "<deleted>"
        try:
            usr = commands.MemberConverter(ctx, user).convert()
            name = usr.name
        except discord.ext.commands.errors.BadArgument as e:
            print(e)
        await bot.say("User {0} sent {1} messages.".format(name, users[user]))


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

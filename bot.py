# /bin/python3
from datetime import datetime

import discord
from discord.ext import commands

from config import *

# prisma = discord.Client()
bot = commands.Bot(command_prefix=PREFIX, help_attrs=HELP_ATTRIBUTES)

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
    await bot.change_presence(game=discord.Game(name="with your heart"))


@bot.command()
async def hello(ctx: commands.Context, *args):
    # print(bot.get_server(295572327826194434).__class__)
    # channel = commands.ChannelConverter(ctx, '322456259897065472').convert()
    # print(channel.name)
    channel = await commands.TextChannelConverter().convert(ctx, args[0])
    limit = args[1]
    users = dict()
    limit = int(limit)
    count = limit
    before = startup
    with ctx.typing():
        while count == limit:
            count = 0
            async for message in channel.history(limit=int(limit), before=before):
                who = message.author.id
                users[who] = users.get(who, 0) + 1
                count = count + 1
                before = message

    for user in users.keys():
        try:
            usr = await commands.MemberConverter().convert(ctx, str(user))
        except discord.ext.commands.errors.BadArgument as e:
            print(e)
            usr = await commands.UserConverter().convert(ctx, str(user))
        await ctx.channel.send("User {0} sent {1} messages.".format(usr.name, users[user]))


@bot.command()
async def load(ctx, *args):
    if ctx.author.id not in ADMIN_USERS:
        return
    if args.__len__() <= 0:
        await ctx.send("No argument passed")
        return
    what = 'cogs.{0}'.format(args[0])
    if not what in extensions:
        extensions.append(what)
    bot.load_extension(what)
    await ctx.send("Extension {0} loaded".format(what))


@bot.command()
async def unload(ctx: commands.Context, *args):
    if ctx.author.id not in ADMIN_USERS:
        return
    if args.__len__() <= 0:
        await ctx.send("No argument passed")
        return
    what = 'cogs.{0}'.format(args[0])
    if what == 'cogs.permisions':
        await ctx.send("Permisions can't be unloaded")
        return
    if what in extensions:
        extensions.remove(what)
        bot.unload_extension(what)
        await ctx.send("Extension {0} uloaded".format(what))
    else:
        await ctx.send("Extension {0} wasn't loaded".format(what))


@bot.command()
async def reload(ctx, *args):
    if ctx.message.author.id not in ADMIN_USERS:
        return
    if args.__len__() <= 0:
        await ctx.send("No argument passed")
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


for ext in extensions:
    bot.load_extension(ext)
bot.remove_command('help')
bot.run(TOKEN)

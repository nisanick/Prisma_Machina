# /bin/python3
from datetime import datetime

import discord
from discord.ext import commands
from database import Database

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
async def test(ctx: commands.Context, *args):
    con = await Database.get_connection()
    async with con.transaction():
        await con.execute("create table if not EXISTS test ( test1 INTEGER PRIMARY KEY,test2 text,test3 INTEGER);")
        await con.execute("insert into test values(1,'first', 50) ON conflict (test1) do update set test3 = test.test3 + 10;")
        await con.execute("insert into test VALUES (2, 'second', 100) ON conflict (test1) do update set test3 = test.test3 + 10;;")
    async with con.transaction():
        async for row in con.cursor("select * from test"):
            print("row {}, text {}, value {}".format(row[0], row['test2'], row[2]))
    await con.close()
    # async with con.transaction():
    #    await con.execute("drop table test")

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


#for ext in extensions:
 #   bot.load_extension(ext)
bot.remove_command('help')
bot.run(TOKEN)

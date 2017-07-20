# /bin/python3
from datetime import datetime

from discord.ext import commands
import database
import asyncio

import config
# from importlib import reload as rld

bot = commands.Bot(command_prefix=config.PREFIX, help_attrs=config.HELP_ATTRIBUTES)

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
    await bot.change_presence()


@bot.command()
async def test(ctx: commands.Context, *args):
    con = await database.Database.get_connection()
    async with con.transaction():
        await con.execute("create table if not EXISTS test ( test1 INTEGER PRIMARY KEY,test2 text,test3 INTEGER);")
        query = "insert into test values($1,$2,$3) ON conflict (test1) do update set test3 = test.test3 + 10;"
        values1 = (1, 'first', 50)
        values2 = (2, 'second', 100)
        await con.execute(query, *values1)
        await con.execute(query, *values2)
    async with con.transaction():
        async for row in con.cursor("select * from test"):
            print("row {}, text {}, value {}".format(row[0], row['test2'], row[2]))
    await con.close()
    # async with con.transaction():
    #    await con.execute("drop table test")


@bot.command()
async def load(ctx, *args):
    if ctx.author.id not in config.ADMIN_USERS:
        return
    if args.__len__() <= 0:
        to_delete = await ctx.send("No argument passed")
        await asyncio.sleep(5)
        await to_delete.delete()
        return
    what = 'cogs.{0}'.format(args[0])
    if not what in extensions:
        extensions.append(what)
    bot.load_extension(what)
    await ctx.send("Extension {0} loaded".format(what))


@bot.command()
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
    if what in extensions:
        extensions.remove(what)
        bot.unload_extension(what)
        await ctx.send("Extension {0} uloaded".format(what))
    else:
        await ctx.send("Extension {0} wasn't loaded".format(what))


@bot.command()
async def reload(ctx, *args):
    if ctx.message.author.id not in config.ADMIN_USERS:
        return
    if args.__len__() <= 0:
        await ctx.send("No argument passed")
        return
    if args[0] == 'all':
        to_reload = extensions
    else:
        to_reload = ["cogs.{0}".format(args[0])]
    for extension in to_reload:
        if extension in extensions:
            await ctx.send('reloading {}'.format(extension))
            bot.unload_extension(extension)
            bot.load_extension(extension)


for ext in extensions:
    bot.load_extension(ext)
bot.remove_command('help')
bot.run(config.TOKEN)

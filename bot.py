# /bin/python3
from datetime import datetime

import discord
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
    enbed = discord.Embed(color=1048560, title="test")
    await ctx.send(embed=enbed)


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

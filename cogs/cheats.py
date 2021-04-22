# coding=utf-8
from datetime import timedelta

import discord
from discord.ext import commands
import asyncio

import config
from TextChecker import TextChecker
from data.rp_texts import cheat_texts
import random
from data.links import inventory_manipulation_link as iml
import database

from web import Web


class Fun(commands.Cog):
    
    cheats = {
        "▒▒▓▓▓▓▒▓▓▓▓▓▓▓▓▓▒▓▓": ('Fuchsia', 'diamonds', 0, 0, 0xFF00FF),
        "░░░░░░░░░░░░░░░░░░░": ('Olive', 'diamonds', 0, 0, 0x808000),
        "░░▒░░▒▒▒░░░░▒▒░░░▒░": ('Green', 'diamonds', 100, 500, 0x66FF00),
        "░▓▓░░▓▓▒▓▒▒▒░░▒▒▓░▒": ('Navy', 'diamonds', -500, -100, 0x000080),
        "▒░░░░▒░░▒▒▒░░░▒▓▒▓░": ('Turquoise', 'diamonds', 1000, 2000, 0x40E0D0),
        "▒▓░░▒▓▓▒░▒▒░░▒░▒▓░░": ('Violet', 'diamonds', -2000, -1000, 0x8F00FF),
        "▓░░░▓░▓▓▒░▓░░▓▓▓▒░░": ('Maroon', 'diamonds', 2000, 5000, 0xB03060),
        "▒▒░░▒▒▓░▒▒▓░░▒▓▓▒░▒": ('Yellow', 'diamonds', -5000, -2000, 0xFFE135),
        "▒░░▒▒░▒▓▒░▒▒▓░░▒▓▓▒": ('Gold', 'diamonds', 1, 10000, 0xFFD700),
        "▓░░▓▓▓▒░░░░░▒▒▓▓░░▒": ('Silver', 'diamonds', -10000, -1, 0xC0C0C0),
        "░▒▒░▒▒░▒▓▓▒▒▓▒▒░▒░░": ('Aqua', 'diamonds', 0, 0, 0x00FFFF),
        "▒▒░▒▒░▒░▒▓░▒▒▓░░░▒▒": ('Lime', 349, 1, 1, 0x00FF00),
        "▒▒░░▒▒▒▒▓▒░░░▒▒▒░▒▓": ('Blue', 412, 5, 5, 0x0000FF),
        "▓▒▒▓▓▒▓▒▒░░▒░▒░▒▒░░": ('Teal', 439, 5, 5, 0x008080),
        "▒░▒▒░░░▒▒▒▒░░▒▒░▒▓▒": ('Emerald', 410, 5, 5, 0x50C878),
        "░░░▒▒▓▓░░▒▒░▓░░▒▓░░": ('Red', 411, 5, 5, 0xFF0038),
        "░░░▒▒▒░▒▓▒▒▓▓▓▓▒▓▓▓": ('Orange', 407, 5, 5, 0xFFA500),
        "░░▓▓▒░░▓▓▒░░▓░▓░▓░▒": ('White', 409, 5, 5, 0xF8F8FF),
        "░░▒▓░▒▓▓▒▓▒░░▒▒░░▒░": ('Bronze', 386, 1, 1, 0xCD7F32),
        "▒░░░▒░▓▒▓░░░▒▒░░▒░░": ('Copper', 302, 1, 1, 0xB87333),
        "▒▒▓░▒▓▒▓░▒▓░▒▓▓░▒▒▒": ('Brass', 271, 1, 1, 0xB5A642),
        "░░▒▒░░░▒░▒░▒▒░░░▒░░": ('Grey', 270, 1, 1, 0x848482),
        "▓▓▓▒░░▒░░▓░▓░░░░░░░": ('Black', 421, 1, 1, 0x292421),
        "░░▓▓░▓░▓▓░▓░░▓░░▓▓▒": ('Pink', 87, 1, 1, 0xFFB7C5),
        "▓░▓▓░▓░▓▓░▓░░▓░░▓▓▓": ('Brown', 261, 1, 1, 0x964B00),
    }
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    @commands.command(aliases=tuple(cheats), hidden=True)
    async def _use_cheat(self, ctx):
        if not isinstance(ctx.channel, discord.DMChannel):
            await ctx.message.delete()
        else:
            await ctx.send("This needs to be used in RP channel.")
            return
        if '💎' not in ctx.channel.name:
            to_delete = await ctx.send("This needs to be used in RP channel.")
            await asyncio.sleep(7)
            await to_delete.delete()
            return
        await self.inventory_manipulation(ctx)

    async def inventory_manipulation(self, ctx):
        db = await database.Database.get_connection(self.bot.loop)
        cooldown_check = "SELECT * FROM cheat_history WHERE user_id = $1 and code = $2 and use > $3"
        cooldown_data = (
            str(ctx.author.id),
            ctx.invoked_with,
            ctx.message.created_at - timedelta(hours=23)
        )
        async with db.transaction():
            async for (user_id, code, last_use) in db.cursor(cooldown_check, *cooldown_data):
                cd_end = last_use + timedelta(hours=23)
                difference = cd_end - ctx.message.created_at
                if difference > timedelta(hours=12):
                    remaining = "almost a day"
                elif difference > timedelta(hours=6):
                    remaining = "less than 12 hours"
                elif difference > timedelta(hours=3):
                    remaining = "less than 6 hours"
                elif difference > timedelta(hours=1):
                    remaining = "less than 3 hours"
                else:
                    remaining = "less than 1 hour"
                to_delete = await ctx.send("You must wait for " + remaining + " to use this command again.")
                await asyncio.sleep(7)
                await to_delete.delete()
                return
        name, item, min_bound, max_bound, colour = self.cheats[ctx.invoked_with]
        text = TextChecker.replace_emotes(cheat_texts[name], self.bot)
        text = text.replace('[CMDR]', ctx.author.mention)
        amount = random.randint(min_bound, max_bound)
        
        embed = discord.Embed(description=text, colour=colour)
        embed.set_author(name=ctx.author.nick or ctx.author.display_name,
                         icon_url=ctx.author.avatar_url)
        
        await ctx.send(embed=embed)
        
        if item is not None:
            values = {
                'item'      : item,
                'quantity'  : amount,
                'hack'      : True,
                'discord_id': ctx.author.id,
                # 'discord_id': 294171600478142466,
                'key'       : config.TRANSACTION_KEY
            }
            response = await Web.get_response(iml, values)
        cheat_history_data = (
            str(ctx.author.id),
            ctx.invoked_with,
            ctx.message.created_at
        )
        await db.execute("INSERT INTO cheat_history VALUES($1, $2, $3)", *cheat_history_data)

def setup(bot: commands.Bot):
    bot.add_cog(Fun(bot))

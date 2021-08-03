import discord
from discord.ext import commands
import asyncio
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import database
from data.links import *
from web import Web


class Stats(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(aliases=['statistics', 'stat', 'stats'])
    async def statistic(self, ctx: commands.Context, *, user=None):
        """Shows statistics of messages and reactions you or specified member sent. Use full name (name#number), ping or ID."""

        if not isinstance(ctx.channel, discord.DMChannel):
            await ctx.message.delete()
        async with ctx.typing():
            if user is None:
                user = ctx.author
            else:
                try:
                    user = await commands.MemberConverter().convert(ctx, user)
                except commands.CommandError:
                    try:
                        user = await commands.UserConverter().convert(ctx, user)
                    except commands.CommandError:
                        await ctx.send(f'{user} not found, showing your stats instead')
                        user = ctx.author
    
            # PREPARE DATA FOR EMBED
    
            message_count = reaction_count = ducks = 0
            total_hunts = previous_hunts = this_hunts = timezone = ''
            words = []
            reactions = []
            today = datetime.utcnow()
            month_ago = today - relativedelta(months=1)
            two_months_ago = today - relativedelta(months=2)
    
            # FROM DB
            limit = 10
            db = await database.Database.get_connection(self.bot.loop)
            user_info = "SELECT message_count, reaction_count, special, ducks, timezone FROM users WHERE user_id = $1"
            words_used = ("SELECT words.word, usage_count, word_count.last_use FROM word_count "
                          "JOIN words ON word_count.word = words.word AND words.excluded = FALSE "
                          "WHERE user_id = $1 ORDER BY usage_count DESC LIMIT $2")
            reactions_used = ("SELECT reactions.reaction, usage_count, reaction_count.last_use, reactions.custom FROM reaction_count "
                              "JOIN reactions ON reaction_count.reaction = reactions.reaction "
                              "WHERE user_id = $1 ORDER BY usage_count DESC LIMIT $2")
            hunt_totals = "SELECT sum(hunted + captured) AS total, sum(hunted) AS h, sum(captured) AS c, sum(first_hunt) AS fh, sum(first_capture) AS fc " \
                          "FROM hunt WHERE user_id = $1"
            hunt_monthly = "SELECT hunted + captured AS total, hunted, captured, first_hunt, first_capture FROM hunt WHERE month = $2 AND year = $3 AND user_id = $1"
            async with db.transaction():
                message_count, reaction_count, special, ducks, timezone = await db.fetchrow(user_info, str(user.id))
                
                async for (word, count, last_use) in db.cursor(words_used, *(str(user.id), limit)):
                    words.append(f'*{word}* | {count}x')
                
                async for (reaction, count, last_use, custom) in db.cursor(reactions_used, *(str(user.id), limit)):
                    if custom:
                        emoji = self.bot.get_emoji(int(reaction))
                        reaction = f"<:{emoji.name}:{emoji.id}>"
                    reactions.append(f'{reaction} | {count}x ({count/reaction_count:.2%})')
                    
                total, hunted, captured, first_hunts, first_captures = await db.fetchrow(hunt_totals, str(user.id)) or (0, 0, 0, 0, 0)
                total_hunts = f'total: {total or 0}\nhunted: {hunted or 0}\ncaptured: {captured or 0}\nfirst hits: {first_hunts or 0}\nfirst caps: {first_captures or 0}'

                previous_total, previous_hunted, previous_captured, previous_first_hunts, previous_first_captures = await db.fetchrow(hunt_monthly, *(str(user.id), two_months_ago.month, two_months_ago.year)) or (0, 0, 0, 0, 0)
                previous_hunts = f'total: {previous_total}\nhunted: {previous_hunted}\ncaptured: {previous_captured}\nfirst hits: {previous_first_hunts}\nfirst caps: {previous_first_captures}'
                this_total, this_hunted, this_captured, this_first_hunts, this_first_captures = await db.fetchrow(hunt_monthly, *(str(user.id), month_ago.month, month_ago.year)) or (0, 0, 0, 0, 0)
                this_hunts = f'total: {this_total}\nhunted: {this_hunted}\ncaptured: {this_captured}\nfirst hits: {this_first_hunts}\nfirst caps: {this_first_captures}'
            await database.Database.close_connection(db)
            
            # FROM WEB
            description = ''
            link = user_data_link
            args = {
                'discord_id': user.id
            }
            response = await Web.get_response(link, args)
            rank = None
            if response['Response'] == 'User not found':
                description = 'Account is not linked'
            else:
                diamonds = int(response['Diamonds'])
                emoji_type = ''
                if count > 200000:
                    emoji_type = 4
                elif count > 50000:
                    emoji_type = 3
                elif count > 10000:
                    emoji_type = 2
                try:
                    emoji = await commands.EmojiConverter().convert(ctx, "diamond{}".format(emoji_type))
                except commands.CommandError:
                    emoji = '💎'
                reputation = int(response['Reputation'])
                if response['Prismatic_rank'] != 'None':
                    rank = response['Prismatic_rank']
                
                description = f'{emoji} {diamonds}\n<:reputation:441778122514366464> {reputation}\nTimezone: {timezone or ""}'
            
            embed = discord.Embed(colour=discord.Colour(0xb85f98), description=description)
            embed.set_thumbnail(url=user.avatar_url)
            
            name = user.name
            if isinstance(user, discord.Member):
                name = user.nick or name
            if rank is not None:
                name = rank + ' ' + name
                
            embed.set_author(icon_url=user.avatar_url, name=name)
            
            embed.add_field(name='Top words', value='\n'.join(words), inline=True)
            embed.add_field(name='Top reactions', value='\n'.join(reactions), inline=True)
            
            embed.add_field(name='Hunt stats', value='🐇', inline=False)
            embed.add_field(name='Total', value=total_hunts, inline=True)
            embed.add_field(name=f'{two_months_ago:%B}', value=previous_hunts, inline=True)
            embed.add_field(name=f'{month_ago:%B}', value=this_hunts, inline=True)
    
            embed.set_footer(text="Joined on ")
            if isinstance(user, discord.Member):
                embed.timestamp = user.joined_at
            await ctx.send(embed=embed)

    @commands.command(aliases=['diamond'])
    async def diamonds(self, ctx, member: discord.Member=None):
        """Shows how many diamonds you or specified member have. Requires linked account! Use full name (name#number), ping or ID."""
        link = user_data_link
        if member is None:
            member = ctx.author

        args = {
            'discord_id': member.id
        }
        response = await Web.get_response(link, args)
        to_delete = [ctx.message]
        sleep = 2
        if response['Response'] == 'User not found':
            if member is ctx.message.author:
                to_delete.append(await ctx.send("❌ This account is not linked"))
            else:
                sleep = 10
                to_delete.append(await ctx.send("❌ Link your account first. Use !link {verification_code} {website_username} . You can find your verification code on website."))
        else:
            count = int(response['Diamonds'])
            emoji_type = ''
            if count > 200000:
                emoji_type = 4
            elif count > 50000:
                emoji_type = 3
            elif count > 10000:
                emoji_type = 2
            try:
                emoji = await commands.EmojiConverter().convert(ctx, "diamond{}".format(emoji_type))
            except commands.CommandError:
                emoji = '💎'
            embed = discord.Embed(description="{} {}".format(emoji, count), color=discord.Colour.blue())
            rank = ""
            if response['Prismatic_rank'] != 'None':
                rank = response['Prismatic_rank']
            embed.set_author(icon_url=member.avatar_url, name="{} {}".format(rank, member.name))
            await ctx.send(embed=embed)
        await asyncio.sleep(sleep)
        if not isinstance(ctx.channel, discord.DMChannel):
            await ctx.channel.delete_messages(to_delete)

    @commands.command()
    async def word(self, ctx: commands.Context, what):
        """Shows usage statistics for specified word"""
        to_delete = [ctx.message]
        what = what.lower().strip()
        db = await database.Database.get_connection(self.bot.loop)

        counts = ("SELECT count(*) AS people, words.word, sum(usage_count) AS count, words.last_use AS use "
                  "FROM word_count "
                  "JOIN words ON word_count.word = words.word "
                  "WHERE words.word = $1 "
                  "GROUP BY words.word")

        times = ("SELECT word_count.last_use, usage_count FROM word_count "
                 "JOIN users ON users.user_id = word_count.user_id "
                 "JOIN words ON word_count.word = words.word "
                 "WHERE users.user_id = $1 AND words.word = $2")

        async with db.transaction():
            try:
                people, word, count, use = await db.fetchrow(counts, what)
                try:
                    last_use, usage = await db.fetchrow(times, *(str(ctx.message.author.id), what))
                except TypeError as e:
                    last_use = None
                    usage = 0
                embed = discord.Embed(title=what, color=13434828,
                                      description="\"{}\" was used {} times by {} people, {} time(s) by you".format(
                                          word, count, people, usage))
                name = ctx.author.name

                if isinstance(ctx.author, discord.Member):
                    name = ctx.author.nick

                embed.set_author(name=name or ctx.author.name, icon_url=ctx.author.avatar_url)
                if usage > 0:
                    embed.add_field(name="Your last use", value="{:%d.%m.%Y %H:%M} (UTC)".format(last_use))
                embed.add_field(name="General last use", value="{:%d.%m.%Y %H:%M} (UTC)".format(use))

            except TypeError as e:
                embed = discord.Embed(title=what, color=13434828, description="\"{}\" was never used before.".format(what))

        await ctx.send("", embed=embed)
        if not isinstance(ctx.channel, discord.DMChannel):
            await ctx.channel.delete_messages(to_delete)
        await database.Database.close_connection(db)


def setup(bot: commands.Bot):
    bot.add_cog(Stats(bot))

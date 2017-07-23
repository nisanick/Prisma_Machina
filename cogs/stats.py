import discord
from discord.ext import commands

import database
from data.links import *
from web import Web


class Stats:
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def statistic(self, ctx: commands.Context, who=None):
        if who is None:
            who = ctx.author
        else:
            try:
                who = await commands.MemberConverter().convert(ctx, who)
            except commands.CommandError:
                who = ctx.author

        limit = 6
        db = await database.Database.get_connection()
        user_info = "SELECT message_count, reaction_count, special FROM users WHERE user_id = $1"
        words_used = ("SELECT words.word, usage_count, word_count.last_use FROM word_count "
                      "JOIN words ON word_count.word = words.word AND words.excluded = FALSE "
                      "WHERE user_id = $1 ORDER BY usage_count DESC LIMIT $2")
        reactions_used = ("SELECT reactions.reaction, usage_count, reaction_count.last_use, reactions.custom FROM reaction_count "
                          "JOIN reactions ON reaction_count.reaction = reactions.reaction "
                          "WHERE user_id = $1 ORDER BY usage_count DESC LIMIT $2")
        async with db.transaction():
            user_id = who.id
            embed = discord.Embed(colour=discord.Colour(0xb85f98))
            embed.set_author(icon_url=who.avatar_url, name=who.name)
            message_count, reaction_count, special = await db.fetchrow(user_info, str(who.id))
            if user_id is 186829544764866560:
                embed.set_footer(text="You said 'By Achenar' {} times.".format(special))
            embed.add_field(name="Message statistics", inline=False,
                            value="You sent {} messages. Top used words:".format(message_count))
            async for (word, count, last_use) in db.cursor(words_used, *(str(user_id), limit)):
                embed.add_field(name=word, inline=True, value="{0:4} time(s), last use: {1}".format(count,
                                                                                                    '{:%d.%m.%Y %H:%M}'.format(
                                                                                                        last_use)))
            embed.add_field(name="Reaction statistics", inline=False,
                            value="You used {} reactions. Top used reactions:".format(reaction_count))
            async for (reaction, count, last_use, custom) in db.cursor(reactions_used, *(str(user_id), limit)):
                emoji = None
                if custom:
                    emoji = self.bot.get_emoji(int(reaction))
                    reaction = "<:{}:{}>".format(emoji.name, emoji.id)
                embed.add_field(name=emoji or reaction, inline=True, value="{0:4} time(s), last use: {1}"
                                .format(count, '{:%d.%m.%Y %H:%M}'.format(last_use)))
            await ctx.send(embed=embed)
            await ctx.message.delete(reason="Command cleanup")

    @commands.command()
    async def diamonds(self, ctx, who=None):
        link = user_data_link
        if who:
            who = await commands.MemberConverter().convert(ctx, who)
        else:
            who = ctx.message.author
        args = {
            'discord_id': who.id
        }
        response = await Web.get_response(link, args)
        count = int(response['Diamonds'])
        emoji_type = ''
        if count > 500:
            emoji_type = 2
        elif count > 2500:
            emoji_type = 3
        elif count > 10000:
            emoji_type = 4
        try:
            emoji = await commands.EmojiConverter().convert(ctx, "diamond{}".format(emoji_type))
        except commands.CommandError as err:
            emoji = '💎'
        embed = discord.Embed(description="{} {}".format(emoji, count), color=discord.Colour.blue())
        embed.set_author(icon_url=who.avatar_url, name=who.name)
        await ctx.send(embed=embed)

    @commands.group()
    async def stat(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            ctx.send("Invalid subcommand!")

    @stat.command()
    async def word(self, ctx: commands.Context, *args):
        if args.__len__() < 1:
            await ctx.send('You must provide a word')
            return
        what = args[0].lower().strip()
        db = await database.Database.get_connection()
        counts = ("SELECT count(*) AS people, words.word, sum(usage_count) AS count, words.last_use "
                  "FROM word_count "
                  "JOIN words ON word_count.word = words.word "
                  "WHERE words.word = $1"
                  "GROUP BY words.word")
        times = ("SELECT word_count.last_use FROM word_count "
                 "JOIN users ON users.user_id = word_count.user_id "
                 "JOIN words ON word_count.word = words.word "
                 "WHERE users.user_id = $1 AND words.word = $2")
        async with db.transaction():
            try:
                people, word, count, use = await db.fetchrow(counts, what)
                last_use = await db.fetchrow(times, *(str(ctx.message.author.id), what))
                await ctx.send("```"
                               "Word {0} was used {1} times by {2} people.\n"
                               "Time of last use: {3:%d.%m.%Y %H:%M}\n"
                               "Time of your last use: {4:%d.%m.%Y %H:%M}"
                               "```".format(word, count, people, use, last_use[0]))
            except TypeError as e:
                print(e)
                await ctx.send("```"
                               "Word {0} was never used before."
                               "```".format(what))


def setup(bot: commands.Bot):
    bot.add_cog(Stats(bot))

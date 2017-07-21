import discord
from datetime import datetime
from discord.ext import commands
import config
import database


class Parser:
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def on_message(self, message: discord.Message):
        if message.author.id == self.bot.user.id or message.content.startswith(tuple(config.PREFIX)):
            return
        what = message.content
        for symbol in config.REPLACEMENTS:
            what = what.replace(symbol, '')
        what = what.replace("\n", " ")
        what = what.split(" ")
        await self.__insert(what, message.author, message.created_at)

    async def on_message_delete(self, message: discord.Message):
        what = message.content
        for symbol in config.REPLACEMENTS:
            what = what.replace(symbol, '')
        what = what.replace("\n", " ")
        what = what.split(" ")
        await self.__delete(what, message.author)
        db = await database.Database.get_connection()
        insert = "INSERT INTO history (message_id, user_id, old, modification_date, type) VALUES ($1, $2, $3, $4, 'delete')"
        values = (
            message.id,
            str(message.author.id),
            message.content,
            datetime.utcnow()
        )
        async with db.transaction():
            await db.execute(insert, *values)

    async def on_message_edit(self, before, after):
        what = before.content
        for symbol in config.REPLACEMENTS:
            what = what.replace(symbol, '')
        if what.__len__() < 1:
            return
        what = what.replace("\n", " ")
        what = what.split(" ")
        when = datetime.utcnow()
        await self.__delete(what, before.author)
        what = after.content
        for symbol in config.REPLACEMENTS:
            what = what.replace(symbol, '')
        what = what.replace("\n", " ")
        what = what.split(" ")
        when = datetime.utcnow()
        await self.__insert(what, after.author, when)

        db = await database.Database.get_connection()
        insert = ("INSERT INTO history (message_id, user_id, old, new, modification_date, type) "
                  "VALUES ($1, $2, $3, $4, $5, 'edit')")
        values = (
            after.id,
            str(before.author.id),
            before.content,
            after.content,
            when
        )
        async with db.transaction():
            await db.execute(insert, *values)

    @commands.group()
    async def stat(self, ctx: commands.Context):
        print('shit')
        if ctx.invoked_subcommand is None:
            ctx.send("Invalid subcommand!")

    @stat.command()
    async def word(self, ctx: commands.Context, *args):
        if args.__len__() < 1:
            await ctx.send('You must provide a word')
            return
        what = args[0].lower()
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

    @stat.command()
    async def me(self, ctx: commands.Context, *args):
        limit = 5
        if args.__len__() > 0:
            limit = int(args[0])
        db = await database.Database.get_connection()
        user_info = "SELECT message_count FROM users WHERE user_id = $1"
        words_used = ("SELECT words.word, usage_count, word_count.last_use FROM word_count "
                      "JOIN words ON word_count.word = words.word AND words.excluded = FALSE "
                      "WHERE user_id = $1 ORDER BY usage_count DESC LIMIT $2")
        async with db.transaction():
            try:
                user_id = ctx.author.id
                message_count = await db.fetchrow(user_info, str(ctx.author.id))
                result = "```Top {} used words by you:\n{:-<61}\n".format(limit, "")
                async for (word, count, last_use) in db.cursor(words_used, *(str(user_id), limit)):
                    stat = "{0:18} : {1:4} time(s), last use: {2}\n"
                    result = result + stat.format(word.replace('```', ''), count, '{:%d.%m.%Y %H:%M}'.format(last_use))
                result = result + "{:-<61}\nYou sent {} messages since I was turned on.```".format("", message_count[0])
                await ctx.send(result)
            except TypeError:
                print('something wrong happened')

    async def __insert(self, what, author: discord.Member, when: datetime):
        db = await database.Database.get_connection()
        insert_word = "INSERT INTO words (word, excluded, last_use) VALUES ($1, $2, $3) ON CONFLICT (word) DO UPDATE SET last_use = $3"
        insert_user = "INSERT INTO users (user_id, message_count) VALUES ($1, 1) ON CONFLICT (user_id) DO UPDATE SET message_count = users.message_count + 1"
        insert_count = ("INSERT INTO word_count (word, user_id, usage_count, last_use) VALUES"
                        "("
                        "(SELECT word FROM words WHERE word = $1),"
                        "(SELECT user_id FROM users WHERE user_id = $2),"
                        "1,"
                        "$3)"
                        "ON CONFLICT (word,user_id) DO UPDATE SET usage_count = word_count.usage_count + 1, last_use = $3")
        async with db.transaction():
            await db.execute(insert_user, str(author.id))
            for word in what:
                word_values = [
                    word.lower(),
                    False,
                    when
                ]
                if word.lower() in config.EXCLUDED:
                    word_values[1] = True
                await db.execute(insert_word, *word_values)
                count_values = (
                    word.lower(),
                    str(author.id),
                    when,
                )
                await db.execute(insert_count, *count_values)

    async def __delete(self, what, author: discord.Member):
        db = await database.Database.get_connection()
        insert_user = "INSERT INTO users (user_id, message_count) VALUES ($1, 0) ON CONFLICT (user_id) DO UPDATE SET message_count = users.message_count - 1"
        insert_count = ("UPDATE word_count SET usage_count = word_count.usage_count - 1 "
                        "WHERE word = $1 AND user_id = $2")
        async with db.transaction():
            await db.execute(insert_user, str(author.id))
            for word in what:
                count_values = (
                    word.lower(),
                    str(author.id)
                )
                await db.execute(insert_count, count_values)


def setup(bot: commands.Bot):
    bot.add_cog(Parser(bot))

import discord
from datetime import datetime
from discord.ext import commands
from config import *
from database import Database


class Parser:
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def on_message(self, message: discord.Message):
        if message.author.id == self.bot.user.id or message.content.startswith(tuple(PREFIX)):
            return
        what = message.content
        for symbol in REPLACEMENTS:
            what = what.replace(symbol, '')
        what = what.replace("\n", " ")
        what = what.split(" ")
        self.__insert(what, message.author, message.created_at)

    async def on_message_delete(self, message: discord.Message):
        what = message.content
        for symbol in REPLACEMENTS:
            what = what.replace(symbol, '')
        what = what.replace("\n", " ")
        what = what.split(" ")
        self.__delete(what, message.author, datetime.utcnow())
        db = Database.get_connection()
        insert = "INSERT INTO history (message_id, user_id, old, modification_date, type) VALUES (%(message_id)s, %(user_id)s, %(content)s, %(now)s, 'delete')"
        values = {
            'message_id': message.id,
            'user_id': message.author.id,
            'content': message.content,
            'now': datetime.utcnow()
        }
        cursor = db.cursor(buffered=True)
        cursor.execute(insert, values)
        cursor.close()
        db.commit()

    async def on_message_edit(self, before, after):
        what = before.content
        for symbol in REPLACEMENTS:
            what = what.replace(symbol, '')
        what = what.replace("\n", " ")
        what = what.split(" ")
        when = datetime.utcnow()
        self.__delete(what, before.author, when)

        what = after.content
        for symbol in REPLACEMENTS:
            what = what.replace(symbol, '')
        what = what.replace("\n", " ")
        what = what.split(" ")
        when = datetime.utcnow()
        self.__insert(what, after.author, when)

        db = Database.get_connection()
        insert = ("INSERT INTO history (message_id, user_id, old, new, modification_date, type) "
                  "VALUES (%(message_id)s, %(user_id)s, %(content_old)s, %(content_new)s, %(now)s, 'edit')")
        values = {
            'message_id': after.id,
            'user_id': before.author.id,
            'content_old': before.content,
            'content_new': after.content,
            'now': when
        }
        cursor = db.cursor(buffered=True)
        cursor.execute(insert, values)
        cursor.close()
        db.commit()

    @commands.group()
    async def stat(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            ctx.send("Invalid subcommand!")

    @stat.command()
    async def word(self, ctx: commands.Context, *args):
        if args.__len__() < 1:
            await ctx.send('You must provide a word')
            return
        what = args[0].lower()
        db = Database.get_connection()
        counts = ("SELECT count(*) as people, words.word, sum(usage_count) as count, words.last_use "
                  "FROM word_count "
                  "JOIN words ON word_count.word = words.word "
                  "WHERE words.word = %s"
                  "GROUP BY words.word")
        cursor_counts = db.cursor(buffered=True)
        cursor_counts.execute(counts, (what,))
        times = ("SELECT word_count.last_use FROM word_count "
                 "JOIN users ON users.user_id = word_count.user_id "
                 "JOIN words ON word_count.word = words.word "
                 "WHERE users.user_id = %(who)s AND words.word = %(what)s")
        cursor_times = db.cursor(buffered=True)
        cursor_times.execute(times, {'who': ctx.message.author.id, 'what': what, })
        try:
            people, word, count, use = cursor_counts.fetchone()
            last_use = cursor_times.fetchone()[0]
            await ctx.send("```"
                           "Word {0} was used {1} times by {2} people.\n"
                           "Time of last use: {3}\n"
                           "Time of your last use: {4}"
                           "```".format(word, count, people, use, last_use))
        except TypeError:
            await ctx.send("```"
                           "Word {0} was never used before."
                           "```".format(what))
        finally:
            cursor_counts.close()
            cursor_times.close()

    @stat.command()
    async def me(self, ctx: commands.Context, *args):
        limit = 5
        if args.__len__() > 0:
            limit = int(args[0])
        db = Database.get_connection()
        user_info = "SELECT message_count FROM users WHERE user_id = %s"
        words_used = ("SELECT words.word, usage_count, word_count.last_use FROM word_count "
                      "JOIN words ON word_count.word = words.word AND words.exclude = FALSE "
                      "WHERE user_id = %s ORDER BY usage_count DESC limit %s")
        cursor = db.cursor(buffered=True)
        cursor.execute(user_info, (ctx.author.id,))
        try:
            user_id = ctx.author.id
            message_count = cursor.fetchone()
            result = "```Top {} used words by you:\n{:-<61}\n".format(limit, "")
            cursor.execute(words_used, (user_id, limit))
            for (word, count, last_use) in cursor:
                stat = "{0:18} : {1:4} time(s), last use: {2}\n"
                result = result + stat.format(word.replace('```', ''), count, '{:%d.%m.%Y %H:%M}'.format(last_use))
            result = result + "{:-<61}\nYou sent {} messages since I was turned on.```".format("", message_count[0])
            await ctx.send(result)
        except TypeError:
            print('something wrong happened')
        finally:
            cursor.close()

    def __insert(self, what, author: discord.Member, when: datetime):
        db = Database.get_connection()
        insert_word = "INSERT INTO words (word, exclude, last_use) VALUES (%(val)s, %(exclude)s, %(now)s) ON DUPLICATE KEY UPDATE words.last_use = %(now)s"
        insert_user = "INSERT INTO users (user_id, message_count) VALUES (%(ident)s, 1) ON DUPLICATE KEY UPDATE users.message_count = message_count + 1"
        insert_count = ("INSERT INTO word_count (word, user_id, usage_count, last_use) VALUES"
                        "("
                        "(SELECT word FROM words WHERE word = %(val)s),"
                        "(SELECT user_id FROM users WHERE user_id = %(ident)s),"
                        "1, %(now)s)"
                        "ON DUPLICATE KEY UPDATE word_count.usage_count = word_count.usage_count + 1, last_use = %(now)s")
        user_values = {
            'ident': author.id,
        }
        cursor = db.cursor()
        cursor.execute(insert_user, user_values)
        for word in what:
            print(word.lower())
            word_values = {
                'val': word.lower() + "",
                'now': when,
                'exclude': False
            }
            if word.lower() in EXCLUDED:
                word_values['exclude'] = True
            cursor.execute(insert_word, word_values)
            count_values = {
                'val': word.lower() + "",
                'ident': author.id,
                'now': when,
            }
            cursor.execute(insert_count, count_values)
        db.commit()

    def __delete(self, what, author: discord.Member, when: datetime):
        db = Database.get_connection()
        insert_user = "INSERT INTO users (user_id, message_count) VALUES (%(ident)s, 0) ON DUPLICATE KEY UPDATE users.message_count = message_count - 1"
        insert_count = ("UPDATE word_count SET word_count.usage_count = word_count.usage_count - 1 "
                        "WHERE word = %(val)s AND user_id = %(ident)s")
        user_values = {
            'ident': author.id,
        }
        cursor = db.cursor()
        cursor.execute(insert_user, user_values)
        for word in what:
            count_values = {
                'val': word.lower(),
                'ident': author.id,
                'now': when,
            }
            cursor.execute(insert_count, count_values)
        db.commit()


def setup(bot: commands.Bot):
    bot.add_cog(Parser(bot))

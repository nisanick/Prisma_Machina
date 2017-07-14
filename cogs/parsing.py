import discord
from datetime import datetime
from discord.ext import commands
from config import *
from database import Database


class Parser:
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def on_message(self, message: discord.Message):
        if not message.author.id == self.bot.user.id and not message.content.startswith("!stat"):
            what = message.content.split(" ")
            self.__insert(what, message.author)

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
        counts = ("SELECT count(*) as people, words.word, sum(count) as count, words.last_use "
                  "FROM word_count "
                  "JOIN words ON word_count.word_id = words.word_id "
                  "WHERE words.word LIKE %s"
                  "GROUP BY words.word")
        cursor_counts = db.cursor(buffered=True)
        cursor_counts.execute(counts, (what,))
        times = ("SELECT word_count.last_use FROM word_count "
                 "JOIN users ON users.user_id = word_count.user_id "
                 "JOIN words ON word_count.word_id = words.word_id "
                 "WHERE users.identity LIKE %(who)s AND words.word LIKE %(what)s")
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
        user_info = "SELECT user_id, message_count FROM users WHERE identity LIKE %s"
        words_used = ("SELECT word, count, word_count.last_use FROM word_count "
                      "JOIN words ON word_count.word_id = words.word_id "
                      "WHERE user_id = %s ORDER BY count DESC limit %s")
        cursor = db.cursor(buffered=True)
        cursor.execute(user_info, (ctx.author.id,))
        try:
            user_id, message_count = cursor.fetchone()
            result = "```Top {} used words by you:\n{:-<61}\n".format(limit, "")
            cursor.execute(words_used, (user_id, limit))
            for (word, count, last_use) in cursor:
                stat = "{0:18} : {1:4} time(s), last use: {2}\n"
                result = result + stat.format(word.replace('```', ''), count, '{:%d.%m.%Y %H:%M}'.format(last_use))
            result = result + "{:-<61}\nYou sent {} messages since I was turned on.```".format("", message_count)
            await ctx.send(result)
        except TypeError:
            print('something wrong happened')
        finally:
            cursor.close()

    def __insert(self, what, author: discord.Member):
        db = Database.get_connection()
        insert_word = "INSERT INTO words (word, last_use) VALUES (%(val)s, %(now)s) ON DUPLICATE KEY UPDATE words.last_use = %(now)s"
        insert_user = "INSERT INTO users (identity, message_count) VALUES (%(ident)s, 1) ON DUPLICATE KEY UPDATE users.message_count = message_count + 1"
        insert_count = ("INSERT INTO word_count (word_id, user_id, count, last_use) VALUES"
                        "("
                        "(SELECT word_id FROM words WHERE word LIKE %(val)s),"
                        "(SELECT user_id FROM users WHERE identity LIKE %(ident)s),"
                        "1, %(now)s)"
                        "ON DUPLICATE KEY UPDATE word_count.count = word_count.count + 1, last_use = %(now)s")
        user_values = {
            'ident': author.id,
        }
        cursor = db.cursor()
        cursor.execute(insert_user, user_values)
        for word in what:
            word_values = {
                'val': word.lower().replace('!', '').replace('?', '').replace(',', '').replace('.', ''),
                'now': datetime.now(),
            }
            cursor.execute(insert_word, word_values)
            count_values = {
                'val': word.lower().replace('!', '').replace('?', '').replace(',', '').replace('.', ''),
                'ident': author.id,
                'now': datetime.now(),
            }
            cursor.execute(insert_count, count_values)
        db.commit()


def setup(bot: commands.Bot):
    bot.add_cog(Parser(bot))

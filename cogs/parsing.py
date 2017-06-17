import discord
from datetime import datetime
from discord.ext import commands
from config import *
from database import Database


class Parser:
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def on_message(self, message: discord.Message):
        if not message.author.id == self.bot.user.id:
            what = message.content.split(" ")
            self.__insert(what, message.author)

    @commands.command(pass_context=True)
    async def stat(self, ctx: commands.Context, *args):
        if args.__len__() < 1:
            await self.bot.say('You must provide a word')
            return
        what = args[0].lower()
        db = Database.get_connection()
        counts = ("SELECT count(*) as people, words.word, sum(count) as count, words.last_use "
                  "FROM word_count "
                  "JOIN words ON word_count.word_id = words.word_id "
                  "WHERE words.word LIKE %s"
                  "GROUP BY words.word")
        cursor_counts = db.cursor(buffered=True)
        cursor_counts.execute(counts,(what,))
        times = ("SELECT word_count.last_use FROM word_count "
                 "JOIN users ON users.user_id = word_count.user_id "
                 "JOIN words ON word_count.word_id = words.word_id "
                 "WHERE users.identity LIKE %(who)s AND words.word LIKE %(what)s")
        cursor_times = db.cursor(buffered=True)
        cursor_times.execute(times,{'who': ctx.message.author.id, 'what': what,})
        people, word, count, use = cursor_counts.fetchone()
        last_use = cursor_times.fetchone()[0]
        await self.bot.say("```"
                           "Word {0} was used {1} times by {2} people.\n"
                           "Time of last use: {3}\n"
                           "Time of your last use: {4}"
                           "```".format(word, count, people, use, last_use))




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
                'val': word.lower(),
                'now': datetime.now(),
            }
            cursor.execute(insert_word, word_values)
            count_values = {
                'val': word.lower(),
                'ident': author.id,
                'now': datetime.now(),
            }
            cursor.execute(insert_count, count_values)
        db.commit()



def setup(bot: commands.Bot):
    bot.add_cog(Parser(bot))

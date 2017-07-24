import discord
from datetime import datetime
from discord.ext import commands
import config
import database
import checks


class Parser:
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    @commands.check(checks.can_manage_bot)
    async def history(self, ctx, channel, before=None):
        limit = 100
        channel = await commands.TextChannelConverter().convert(ctx, channel)
        count = limit
        if before:
            last = datetime.utcfromtimestamp(float(before))
        else:
            last = None
        async with channel.typing():
            while count == limit:
                count = 0
                async for message in channel.history(limit=limit, before=last):
                    last = message
                    what = message.content
                    what = what.replace("\n", " ")
                    if message.author.id is 186829544764866560:
                        await self.techeron_check(what)
                    what = what.split(" ")
                    await self.__insert(what, message.author, message.created_at, history=True)
                    for reaction in message.reactions:
                        async for user in reaction.users():
                            await self.__insert_reaction(reaction, user, message.created_at, history=True)
                    count = count + 1
        await ctx.send("History of {} added.".format(channel.name))

    async def on_message(self, message: discord.Message):
        if message.author.id == self.bot.user.id or message.content.startswith(tuple(config.PREFIX)):
            return
        what = message.content
        what = what.replace("\n", " ")
        if message.author.id is 186829544764866560:
            await self.techeron_check(what)
        what = what.split(" ")
        await self.__insert(what, message.author, message.created_at)

    async def on_message_delete(self, message: discord.Message):
        if message.author.id == self.bot.user.id or message.content.startswith(tuple(config.PREFIX)):
            return
        what = message.content
        what = what.replace("\n", " ")
        what = what.split(" ")
        await self.__delete(what, message.author)
        db = await database.Database.get_connection()
        insert = "INSERT INTO history (message_id, user_id, old, modification_date, type) VALUES ($1, $2, $3, $4, 'delete')"
        values = (
            str(message.id),
            str(message.author.id),
            message.content,
            datetime.utcnow()
        )
        async with db.transaction():
            await db.execute(insert, *values)

    async def on_message_edit(self, before, after):
        if before.author.id == self.bot.user.id or before.content.startswith(tuple(config.PREFIX)):
            return
        what = before.content
        if what.__len__() < 1:
            return
        what = what.replace("\n", " ")
        what = what.split(" ")
        when = datetime.utcnow()
        await self.__delete(what, before.author)
        what = after.content
        what = what.replace("\n", " ")
        what = what.split(" ")
        when = datetime.utcnow()
        await self.__insert(what, after.author, when)

        db = await database.Database.get_connection()
        insert = ("INSERT INTO history (message_id, user_id, old, new, modification_date, type) "
                  "VALUES ($1, $2, $3, $4, $5, 'edit')")
        values = (
            str(after.id),
            str(before.author.id),
            before.content,
            after.content,
            when
        )
        async with db.transaction():
            await db.execute(insert, *values)

    async def on_reaction_add(self, reaction, user):
        if user.bot:
            return
        await self.__insert_reaction(reaction, user, datetime.utcnow())

    async def on_reaction_remove(self, reaction, user):
        if user.bot:
            return
        await self.__delete_reaction(reaction, user)

    async def techeron_check(self, message):
        text = "by achenar"
        if not message.lower().__contains__(text):
            return
        insert = "INSERT INTO users (user_id, message_count, reaction_count, special) VALUES ($1, 0, 0, 1) ON CONFLICT (user_id) DO UPDATE SET special = users.special + 1"
        db = await database.Database.get_connection()
        async with db.transaction():
            await db.execute(insert, str(186829544764866560))

    async def __insert(self, what, author: discord.Member, when: datetime, history=False):
        db = await database.Database.get_connection()
        insert_word = "INSERT INTO words (word, excluded, last_use) VALUES ($1, $2, $3) ON CONFLICT (word) DO UPDATE SET last_use = $3"
        insert_user = "INSERT INTO users (user_id, message_count, reaction_count) VALUES ($1, 1, 0) ON CONFLICT (user_id) DO UPDATE SET message_count = users.message_count + 1"
        insert_count = ("INSERT INTO word_count (word, user_id, usage_count, last_use) VALUES($1, $2, 1, $3)"
                        "ON CONFLICT (word,user_id) DO UPDATE SET usage_count = word_count.usage_count + 1, last_use = $3")
        if history:
            insert_word = "INSERT INTO words (word, excluded, last_use) VALUES ($1, $2, $3) ON CONFLICT DO NOTHING "
            insert_count = ("INSERT INTO word_count (word, user_id, usage_count, last_use) VALUES($1, $2, 1, $3)"
                            "ON CONFLICT (word,user_id) DO UPDATE SET usage_count = word_count.usage_count + 1")
        async with db.transaction():
            await db.execute(insert_user, str(author.id))
            replaced = []
            for word in what:
                if not word.startswith("<"):
                    for symbol in config.REPLACEMENTS:
                        word = word.replace(symbol, ' ')
                replaced.append(word)
            what = " ".join(replaced)
            what = what.split(" ")
            for word in what:
                word_values = [
                    word.lower().strip(),
                    False,
                    when
                ]
                if word.lower().strip() in config.EXCLUDED:
                    word_values[1] = True

                await db.execute(insert_word, *word_values)
                count_values = (
                    word.lower().strip(),
                    str(author.id),
                    when,
                )
                await db.execute(insert_count, *count_values)

    async def __delete(self, what, author: discord.Member):
        db = await database.Database.get_connection()
        insert_user = "INSERT INTO users (user_id, message_count, reaction_count) VALUES ($1, 0, 0) ON CONFLICT (user_id) DO UPDATE SET message_count = users.message_count - 1"
        insert_count = ("UPDATE word_count SET usage_count = word_count.usage_count - 1 "
                        "WHERE word = $1 AND user_id = $2")
        async with db.transaction():
            await db.execute(insert_user, str(author.id))
            replaced = []
            for word in what:
                if not word.startswith("<"):
                    for symbol in config.REPLACEMENTS:
                        word = word.replace(symbol, ' ')
                replaced.append(word)
            what = " ".join(replaced)
            what = what.split(" ")
            for word in what:
                count_values = (
                    word.lower().strip(),
                    str(author.id)
                )
                await db.execute(insert_count, *count_values)

    async def __insert_reaction(self, reaction, who, when, history=False):
        insert_reaction = "INSERT INTO reactions(reaction, custom, last_use) VALUES ($1, $2, $3) ON CONFLICT (reaction) DO UPDATE SET last_use = $3"
        insert_user = "INSERT INTO users (user_id, message_count, reaction_count) VALUES ($1, 0, 1) ON CONFLICT (user_id) DO UPDATE SET reaction_count = users.reaction_count + 1"
        insert_count = ("INSERT INTO reaction_count(reaction, user_id, usage_count, last_use) VALUES ($1, $2, 1, $3)"
                        "ON CONFLICT (reaction, user_id) DO UPDATE SET usage_count = reaction_count.usage_count + 1, last_use = $3")
        if history:
            insert_reaction = "INSERT INTO reactions(reaction, custom, last_use) VALUES ($1, $2, $3) ON CONFLICT DO NOTHING "
            insert_count = ("INSERT INTO reaction_count(reaction, user_id, usage_count, last_use) VALUES ($1, $2, 1, $3)"
                            "ON CONFLICT (reaction, user_id) DO UPDATE SET usage_count = reaction_count.usage_count + 1")
        db = await database.Database.get_connection()
        async with db.transaction():
            await db.execute(insert_user, str(who.id))
            if isinstance(reaction.emoji, discord.Emoji):
                emoji = str(reaction.emoji.id)
                custom = True
            else:
                emoji = reaction.emoji
                custom = False
            reaction_data = (
                emoji,
                custom,
                when
            )
            await db.execute(insert_reaction, *reaction_data)
            count_data = (
                emoji,
                str(who.id),
                when
            )
            await db.execute(insert_count, *count_data)

    async def __delete_reaction(self, reaction, who):
        insert_user = "INSERT INTO users (user_id, message_count, reaction_count) VALUES ($1, 0, 0) ON CONFLICT (user_id) DO UPDATE SET reaction_count = users.reaction_count - 1"
        delete_count = "UPDATE reaction_count SET usage_count = usage_count - 1 WHERE reaction = $1 AND user_id = $2"
        db = await database.Database.get_connection()
        async with db.transaction():
            await db.execute(insert_user, str(who.id))
            if isinstance(reaction.emoji, discord.Emoji):
                emoji = str(reaction.emoji.id)
            else:
                emoji = reaction.emoji
            reaction_data = (
                emoji,
                str(who.id)
            )
            await db.execute(delete_count, *reaction_data)


def setup(bot: commands.Bot):
    bot.add_cog(Parser(bot))

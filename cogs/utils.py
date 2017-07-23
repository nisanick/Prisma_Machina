import asyncio
import random
from datetime import datetime

import discord
from discord.ext import commands

import checks
import database
from paginator import HelpPaginator, CannotPaginate
import config
from web import Web

class Utils:
    def __init__(self, bot):
        self.bot = bot

    async def on_ready(self):
        # await self.timer(1)
        pass

    @commands.command(name='help')
    async def _help(self, ctx, *, command: str = None):
        """Shows help about a command or the bot"""

        try:
            if command is None:
                p = await HelpPaginator.from_bot(ctx)
            else:
                entity = self.bot.get_cog(command) or self.bot.get_command(command)

                if entity is None:
                    return await ctx.send(f'Command "{command}" not found.')
                elif isinstance(entity, commands.Command):
                    p = await HelpPaginator.from_command(ctx, entity)
                else:
                    p = await HelpPaginator.from_cog(ctx, entity)

            await p.paginate()
        except CannotPaginate as e:
            await ctx.send(e)

    @commands.command()
    async def time(self, ctx):
        year = datetime.now().timetuple().tm_year
        now = datetime.utcnow().replace(year=(year + 1286)).strftime("%H:%M %d %b %Y")
        await ctx.send(now)

    @commands.command()
    async def link(self, ctx, verification, *, account):
        link = 'http://www.prismatic-imperium.com/api/link_account.php'
        args = {
            'discord_id': ctx.message.author.id,
            'username': account,
            'verification': verification,
            'discord_name': "{}#{}".format(ctx.message.author.name, ctx.message.author.discriminator)
        }
        response = await Web.get_response(link, args)
        to_delete = [ctx.message]
        if response['response'] == 'User not found':
            to_delete.append(
                await ctx.send('❌ Please register on our website first\nhttp://www.prismatic-imperium.com/reg_form.php'))
        elif response['response'] == 'Invalid Verification Code':
            to_delete.append(
                await ctx.send('❌ Check your verification code and try again.'))
        elif response['response'] == 'Success':
            to_delete.append(
                await ctx.send('✅'))
        elif response['response'] == 'Account is already linked':
            to_delete.append(
                await ctx.send('❌ This account is already linked to Discord.'))
        await asyncio.sleep(5)
        await ctx.channel.delete_messages(to_delete, reason="Deletion of unneeded messages.")

    async def on_member_join(self, member: discord.Member):
        channel = self.bot.get_channel(config.ANNOUNCE_CHANNEL)
        await channel.send(config.WELCOME.format(member.mention))
        for role in member.guild.roles:
            if role.name == 'High Council':
                mention = role.mention
        await self.bot.get_channel(config.ADMINISTRATION_CHANNEL).send("{} just joined the server. {}".format(member.mention, mention))

    async def on_member_remove(self, member):
        channel = self.bot.get_channel(config.ANNOUNCE_CHANNEL)
        await channel.send('{} left the server'.format(member.mention))


'''
    async def timer(self, delay):
        await asyncio.sleep(delay)
        print('timer')
        db = await database.Database.get_connection()
        query_event = "SELECT event_id, event_type FROM schedule WHERE event_time <= %(when)s AND done = FALSE"
        query_update = "UPDATE schedule SET done = TRUE WHERE event_id = %(id)s"
        data = {
            'when': datetime.utcnow(),
            'id': 0
        }
        events = db.cursor(buffered=True)
        events.execute(query_event, data)
        for event_id, event_type in events:
            data['id'] = event_id
            if event_type is 0:
                await self.timed_message()
            db.cursor().execute(query_update, data)
            db.commit()
        await self.timer(60)

    async def timed_message(self):
        db = Database.get_connection()
        query_message = "SELECT message_content FROM messages ORDER BY RAND() LIMIT 1"
        query_insert = "INSERT INTO schedule (done, event_type, event_time) VALUES (FALSE, 0, %(when)s)"
        new_delay = random.randint(43200, 86400)
        stamp = datetime.utcnow().timestamp() + new_delay
        print(datetime.fromtimestamp(stamp))
        data = {
            'when': datetime.fromtimestamp(stamp)
        }
        message = db.cursor(buffered=True)
        message.execute(query_message)
        content = message.fetchone()[0]
        # TODO - maybe not more than 1 channel
        for channel_id in config.TIMED_MESSAGE_CHANNELS:
            channel = self.bot.get_channel(channel_id)
            await channel.send(content)
        db.cursor().execute(query_insert, data)
        db.commit()'''


def setup(bot):
    bot.add_cog(Utils(bot))

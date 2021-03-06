import datetime
import traceback

import discord
from discord.ext import commands

import config
import asyncio


class AssBotException(Exception):
    pass


class ResponseStatusError(AssBotException):
    def __init__(self, status, reason, url):
        msg = 'REQUEST::[STATUS TOO HIGH    ]: {} - {} - [[{}]]'.format(status, reason, url)
        super().__init__(msg)


class CommandErrorHandler(commands.Cog):
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """The event triggered when an error is raised while invoking a command.
        ctx   : Context
        error : Exception"""

        to_delete = []

        error = getattr(error, 'original', error)

        ignored = commands.CommandNotFound
        if isinstance(error, ignored):
            to_delete.append(await ctx.send('This command doesn\'t exist.'))
            await asyncio.sleep(7)
            if not isinstance(ctx.channel, discord.DMChannel):
                await ctx.channel.delete_messages(to_delete)
            return
        else:
            message = "<@163037317278203908>"
            to_delete.append(ctx.message)

        handler = {
            discord.Forbidden: '**I do not have the required permissions to run this command.**',
            commands.DisabledCommand: '{} has been disabled.'.format(ctx.command),
            commands.NoPrivateMessage: '{} can not be used in Private Messages.'.format(ctx.command),
            commands.CheckFailure: '**You aren\'t allowed to use this command!**'
        }

        try:
            message = handler[type(error)]
        except KeyError:
            to_delete.append(await ctx.send('❌ Your command couldn\'t be processed. Please refer to [p]help command. ❌'))
        else:
            to_delete.append(await ctx.send(message))

        await asyncio.sleep(7)
        if not isinstance(ctx.channel, discord.DMChannel):
            await ctx.channel.delete_messages(to_delete)

        embed = discord.Embed(title='Command Exception', color=discord.Color.red())
        embed.set_footer(text='Occured on')
        embed.timestamp = datetime.datetime.utcnow()

        exc = ''.join(traceback.format_exception(type(error), error, error.__traceback__, chain=False))
        exc = exc.replace('`', '\u200b`')
        embed.description = '```py\n{}\n```'.format(exc)

        embed.add_field(name='Command', value=ctx.command.qualified_name)
        embed.add_field(name='Invoker', value=ctx.author)
        embed.add_field(name='Location', value='Channel: {0.channel}'.format(ctx))
        embed.add_field(name='Message', value=ctx.message.content)

        for channel in config.ERROR_CHANNELS:
            await ctx.bot.get_channel(channel).send(message, embed=embed)


def setup(bot):
    bot.add_cog(CommandErrorHandler())


import traceback
import sys
import discord.ext
import asyncio
import config


class CommandErrorHandler:
    def __init__(self, bot):
        self.bot = bot

    async def on_command_error(self, ctx, error):
        """The event triggered when an error is raised while invoking a command.
        ctx   : Context
        error : Exception"""

        to_delete = [ctx.message]
        channel = await discord.ext.commands.TextChannelConverter().convert(ctx, config.ADMINISTRATION_CHANNEL)

        if isinstance(error, discord.ext.commands.CommandNotFound):
            await self.clean_after_error(ctx, to_delete)
            return

        try:
            if isinstance(error.original, discord.errors.Forbidden):
                to_delete.append(await ctx.send('**I do not have the required permissions to run this command.**'))
        except AttributeError:
            pass

        if isinstance(error, discord.ext.commands.DisabledCommand):
            try:
                await ctx.send('{} has been disabled.'.format(ctx.command))
            except:
                pass
            finally:
                await self.clean_after_error(ctx, to_delete)
                return

        if isinstance(error, discord.ext.commands.NoPrivateMessage):
            try:
                await ctx.author.send('{} can not be used in Private Messages.'.format(ctx.command))
            except:
                pass
            finally:
                await self.clean_after_error(ctx, to_delete)
                return

        if isinstance(error, discord.ext.commands.BadArgument):
            print(ctx.command.qualified_name)
            if ctx.command.qualified_name == 'diamonds':
                return await ctx.send('I could not find that member. Please try again.')

        await self.clean_after_error(ctx, to_delete)

        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    async def clean_after_error(self, ctx, to_delete):
        await asyncio.sleep(5)
        await ctx.channel.delete_messages(to_delete)


def setup(bot):
    bot.add_cog(CommandErrorHandler(bot))

from web import Web
from discord.ext import commands
import discord
import asyncio
from data.links import donation_link
import config
import checks


class Transactions:
    def __init__(self, bot):
        self.bot = bot
        self.author = None
        self.message = None
        self.process_transaction = True

    @commands.command(aliases=['give', 'donation'])
    async def donate(self, ctx: commands.Context, amount, *, who: discord.Member):
        """Gives {amount} of diamonds from your account to whoever you choose. Requires linked accounts!"""
        await self.transaction(ctx, amount, ctx.author, who)

    @commands.command(hidden=True)
    @commands.check(checks.can_manage_bot)
    async def take(self, ctx, amount, *, who: discord.Member):
        try:
            member = await commands.MemberConverter().convert(ctx, '294171600478142466')
        except commands.CommandError:
            member = ctx.author
        await self.transaction(ctx, amount,  who, member)

    def react_check(self, reaction, user):
        if user is None or user.id != self.author.id:
            return False

        if reaction.message.id != self.message.id:
            return False

        for emoji, process in [('❌', False), ('✅', True)]:
            if reaction.emoji == emoji:
                self.process_transaction = process
                return True
        return False

    async def transaction(self, ctx, amount, giver: discord.Member, receiver: discord.Member):
        to_delete = []
        if giver.id == receiver.id:
            await ctx.message.add_reaction('😏')
            return

        self.author = ctx.author
        self.message = ctx.message

        await ctx.message.add_reaction('✅')
        await ctx.message.add_reaction('❌')

        try:
            reaction, user = await self.bot.wait_for('reaction_add', check=self.react_check, timeout=30.0)
        except asyncio.TimeoutError:
            await ctx.message.clear_reactions()
            await ctx.message.add_reaction('❌')
            return
        await ctx.message.clear_reactions()

        if not self.process_transaction:
            await ctx.message.add_reaction('❌')
        else:
            try:
                if int(amount) < 1:
                    raise ValueError
                else:

                    values = {
                        'giver': giver.id,
                        'receiver': receiver.id,
                        'amount': amount
                    }
                    response = await Web.get_response(donation_link, values)
                    if response['Donation'] == 'Failed':
                        await ctx.message.add_reaction('❌')
                        if response['Giver'] == 'Giver not found':
                            to_delete.append(await ctx.send(
                                "Your account is not linked! Please follow instructions on our website to link your account."))
                        elif response['Receiver'] == 'Receiver not found':
                            to_delete.append(
                                await ctx.send("{} don't have their account linked!".format(receiver.nick or receiver.name)))
                    elif response['Donation'] == 'Not Enough Diamonds':
                        await ctx.message.add_reaction('❌')
                        to_delete.append(await ctx.send("Not enough diamonds"))
                    else:
                        emoji = self.bot.get_emoji(352874998618128384)
                        await ctx.message.add_reaction(emoji)
                        admin_channel = await commands.TextChannelConverter().convert(ctx, config.ADMINISTRATION_CHANNEL)
                        await admin_channel.send(
                            "{} diamonds went from {} to {}".format(amount, giver.nick or giver.name,
                                                                    receiver.nick or receiver.name))
            except ValueError:
                to_delete.append(ctx.message)
                to_delete.append(await ctx.send('Invalid amount'))
        await asyncio.sleep(5)
        if not isinstance(ctx.channel, discord.DMChannel):
            await ctx.channel.delete_messages(to_delete)


def setup(bot):
    bot.add_cog(Transactions(bot))

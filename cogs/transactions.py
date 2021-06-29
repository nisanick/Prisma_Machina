from web import Web
from discord.ext import commands
import discord
import asyncio
from data.links import donation_link, award_link
import config
import checks


class Transactions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.donations = []
        self.process_transaction = True
    
    @commands.group(name='award', case_insensitive=True)
    @commands.check(checks.can_manage_bot)
    async def _award(self, ctx):
        """
        *Admin only* | Set of commands to award members with diamonds and reputation. `?help award` for more info.
        
        Here is a list of all possible subcommands:
        """
        to_delete = [ctx.message]
        if ctx.invoked_subcommand is None:
            to_delete.append(await ctx.send("Subcommand required!"))
            await asyncio.sleep(2)
            if not isinstance(ctx.channel, discord.DMChannel):
                await ctx.channel.delete_messages(to_delete)
    
    @_award.command(name='diamonds', aliases=['d'], case_insensitive=True)
    @commands.check(checks.can_manage_bot)
    async def _diamonds(self, ctx: commands.Context, amount, *, who: discord.Member):
        """
        *Admin only* | Awards specified amount of diamonds to the member. Diamonds can be shortened to 'd'.
        """
        await self.transaction(ctx, amount, ctx.author, who, award_link, 'diamonds')
    
    @_award.command(name='reputation', aliases=['r', 'rep'], case_insensitive=True)
    @commands.check(checks.can_manage_bot)
    async def _reputation(self, ctx: commands.Context, amount, *, who: discord.Member):
        """
        *Admin only* | Awards specified amount of reputation to the member. Reputation can be shortened to 'r' or 'rep'.
        """
        if int(amount) < 1:
            await ctx.message.add_reaction('😏')
            return
        await self.transaction(ctx, amount, ctx.author, who, award_link, 'rep')
    
    @_award.command(name='both', aliases=['b'], case_insensitive=True)
    @commands.check(checks.can_manage_bot)
    async def _both(self, ctx: commands.Context, amount, *, who: discord.Member):
        """
        *Admin only* | Awards specified amount of both diamonds and reputation to the member. Both can be shortened to 'b'.
        """
        if int(amount) < 1:
            await ctx.message.add_reaction('😏')
            return
        await self.transaction(ctx, amount, ctx.author, who, award_link, 'both')
    
    @commands.command(name='donate', aliases=['give', 'donation'], case_insensitive=True)
    async def _donate(self, ctx: commands.Context, amount, *, who: discord.Member):
        """
        Transfers specified amount of diamonds from your account to target member. Use full name (name#number), ping or ID. Amount can only be positive. This command can be also called with `?give` and `?donation`.
        """
        if ctx.author.id == who.id or int(amount) < 1 or who.id == 163037317278203908:
            await ctx.message.add_reaction('😏')
            return
        await self.transaction(ctx, amount, ctx.author, who)
    
    def react_check(self, reaction, user):
        message = reaction.message
        if reaction.message in self.donations:
            
            if user is not None and message.author.id == user.id:
                
                for emoji, process in [('❌', False), ('✅', True)]:
                    
                    if reaction.emoji == emoji:
                        self.process_transaction = process
                        self.donations.remove(message)
                        return True
        
        return False
    
    async def transaction(self, ctx, amount, giver: discord.Member, receiver: discord.Member, endpoint=donation_link,
                          transaction_type='diamonds'):
        to_delete = []
        
        self.donations.append(ctx.message)
        
        await ctx.message.add_reaction('✅')
        await ctx.message.add_reaction('❌')
        
        try:
            await self.bot.wait_for('reaction_add', check=self.react_check, timeout=30.0)
        except asyncio.TimeoutError:
            await ctx.message.clear_reactions()
            await ctx.message.add_reaction('❌')
            return
        await ctx.message.clear_reactions()
        
        if not self.process_transaction:
            await ctx.message.add_reaction('❌')
        else:
            try:
                values = {
                    'giver'   : giver.id,
                    'receiver': receiver.id,
                    'amount'  : amount,
                    'key'     : config.TRANSACTION_KEY,
                    'type'    : transaction_type
                }
                response = await Web.get_response(endpoint, values)
                code = response['Code']
                
                '''
                diamonds_donation
                    0: Success
                    1: Giver not found
                    2: Receiver not found
                    3: Not Enough Diamonds
                    4: Exceeding daily donation limit

                award
                    0: Success
                    1: Giver not found
                    2: Receiver not found
                    3: Unknown type
                '''
                
                if code == 0:
                    emoji = self.bot.get_emoji(352874998618128384)
                    await ctx.message.add_reaction(emoji)
                    admin_channel = await commands.TextChannelConverter().convert(ctx,
                                                                                  config.ADMINISTRATION_CHANNEL)
                    
                    operation = 'donated'
                    if endpoint is award_link:
                        operation = 'awarded'
                    await admin_channel.send(
                        "{} {} {} {} to {}".format(giver.nick or giver.name, operation, amount, transaction_type,
                                                     receiver.nick or receiver.name))
                else:
                    await ctx.message.add_reaction('❌')
                    if code == 1:
                        to_delete.append(await ctx.send(
                            "Your account is not linked! Please follow instructions on our website to link your account."))
                    elif code == 2:
                        to_delete.append(
                            await ctx.send(
                                "{} don't have their account linked!".format(receiver.nick or receiver.name)))
                    elif code == 3:
                        to_delete.append(await ctx.send("Not enough diamonds"))
                    elif code == 4:
                        to_delete.append(await ctx.send("Exceeding daily donation limit"))
            
            except ValueError:
                to_delete.append(ctx.message)
                to_delete.append(await ctx.send('Invalid amount'))
        await asyncio.sleep(5)
        if not isinstance(ctx.channel, discord.DMChannel):
            await ctx.channel.delete_messages(to_delete)


def setup(bot):
    bot.add_cog(Transactions(bot))

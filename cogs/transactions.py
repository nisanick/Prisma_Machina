from web import Web
from discord.ext import commands
import discord
import asyncio
from data.links import donation_link
import config


class Transactions:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def donate(self, ctx: commands.Context, amount, *, who):
        """Gives {amount} of diamonds from your account to whoever you choose. Requires linked accounts!"""
        to_delete = []
        member = await commands.MemberConverter().convert(ctx, who)
        if ctx.author.id == member.id:
            await ctx.message.add_reaction('😏')
            return
        try:
            if int(amount) < 1:
                raise ValueError
            else:
                values = {
                    'giver': ctx.author.id,
                    'receiver': member.id,
                    'amount': amount
                }
                response = await Web.get_response(donation_link, values)
                if response['Donation'] == 'Failed':
                    await ctx.message.add_reaction('❌')
                    if response['Giver'] == 'Giver not found':
                        to_delete.append(await ctx.send("Your account is not linked! Please follow instructions on our website to link your account."))
                    elif response['Receiver'] == 'Receiver not found':
                        to_delete.append(await ctx.send("{} don't have their account linked!".format(member.nick or member.name)))
                elif response['Donation'] == 'Not Enough Diamonds':
                    await ctx.message.add_reaction('❌')
                    to_delete.append(await ctx.send("Not enough diamonds"))
                else:
                    await ctx.message.add_reaction('✅')
                    admin_channel = await commands.TextChannelConverter().convert(ctx, config.ADMINISTRATION_CHANNEL)
                    await admin_channel.send("{} donated {} diamonds to {}".format(ctx.author.nick or ctx.author.name, amount, member.nick or member.name))
        except ValueError:
            to_delete.append(ctx.message)
            to_delete.append(await ctx.send('Invalid amount'))
        await asyncio.sleep(5)
        if not isinstance(ctx.channel, discord.DMChannel):
            await ctx.channel.delete_messages(to_delete, reason="Command cleanup.")


def setup(bot):
    bot.add_cog(Transactions(bot))

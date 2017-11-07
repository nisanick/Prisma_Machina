import asyncio
import random

from checks import *
from data.rp_texts import *

import discord
from discord.ext import commands


class Roleplay:
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.delta = 10

    @commands.group(name='rp')
    async def _rp(self, ctx):
        """
        Base command for RP utilities. Use !help rp for details.
        Mind that parameters [who] [channel] are admin exclusive.
        """
        await ctx.message.delete()
        if ctx.invoked_subcommand is None:
            await ctx.send("Subcommand required!")

    @_rp.command(name="hack")
    async def _hack(self, ctx, difficulty: int, who=None, channel: discord.TextChannel=None):
        """
        Initiates hack with specified difficulty.
        """
        if not await can_manage_bot(ctx):
            who = None
            channel = None
            difficulty = abs(difficulty)

        if difficulty > 0:
            limit = 50
        else:
            limit = -1

        who = who or ctx.message.author
        channel = channel or ctx.channel

        embed = discord.Embed(title="**::Hacking sequence initiated for Security Level {}::**".format(abs(difficulty)),
                              description=("<:rp_utility1:371816529458626570> Encryption Cracking Unit paired with device.\n"
                                           "<:rp_utility1:371816529458626570> Emulation Program Functional.\n"
                                           "<:rp_utility1:371816529458626570> Data Package Compilation Program Functional.\n"
                                           "<:rp_utility1:371816529458626570> Virus Defense Program Functional."),
                              colour=discord.Colour.orange())
        if isinstance(who, discord.Member):
            embed.set_author(name=who.nick or who.display_name, icon_url=who.avatar_url)
        else:
            embed.set_author(name=who)
        message = await channel.send('', embed=embed)
        await asyncio.sleep(self.delta)

        for i in range(abs(difficulty)):
            if i > 0:
                embed.remove_field(0)
                await asyncio.sleep(self.delta)

            prob = random.randint(0, 100)

            if prob > limit:
                embed.add_field(name="**[Core Process {} of {}]**".format(i+1, abs(difficulty)), value=hacks_pass[i].format(embed.author.name), inline=False)
                await message.edit(embed=embed)
            else:
                embed.add_field(name="**[Core Process {} of {}]**".format(i+1, abs(difficulty)), value=hacks_fail[i].format(embed.author.name), inline=False)
                await message.edit(embed=embed)
                await asyncio.sleep(self.delta)
                embed.colour = discord.Colour.red()
                embed.add_field(name="**::Hacking sequence failed::**",
                                value=("<:rp_utility0:371816528326164490> Encryption Cracking Unit disconnected from device.\n"
                                       "<:rp_utility0:371816528326164490> Emulation Program was locked out of the system.\n"
                                       "<:rp_utility0:371816528326164490> Data Package Failed, purging corrupted data.\n"
                                       "<:rp_utility1:371816529458626570> All hostile viruses quarantined and purged.\n"
                                       "<:rp_utility1:371816529458626570> Heat Surge Detected.\n"
                                       "Allow **30 seconds** for utility to cool for optimal performance."))
                await message.edit(embed=embed)
                return

        await asyncio.sleep(self.delta)
        embed.colour = discord.Colour.green()
        embed.add_field(name="**::Hacking sequence was completed successfully::**",
                        value=("<:rp_utility1:371816529458626570> Encryption Cracking Unit paired with device.\n"
                               "<:rp_utility1:371816529458626570> Emulation Program Operated Successfully.\n"
                               "<:rp_utility1:371816529458626570> Data Package Created, ready for download to memory drive.\n"
                               "<:rp_utility1:371816529458626570> All hostile viruses quarantined and purged.\n"
                               "<:rp_utility1:371816529458626570> Heat Surge Detected.\n"
                               "Allow **60 seconds** for utility to cool for optimal performance."))
        await message.edit(embed=embed)

    @_rp.command(name='scb')
    async def _scb(self, ctx, who=None, channel: discord.TextChannel = None):
        """
         Activates Shield Cell Bank.
        """
        if not await can_manage_bot(ctx):
            who = None
            channel = None

        who = who or ctx.message.author
        channel = channel or ctx.channel

        chance = random.randint(1, 100)
        embed = discord.Embed(title="**::Shield Cell Bank::**")

        if isinstance(who, discord.Member):
            embed.set_author(name=who.nick or who.display_name, icon_url=who.avatar_url)
        else:
            embed.set_author(name=who)

        if chance <= 60:
            embed.description = ("Processing…\n"
                                 "Processing…\n"
                                 "Processing…\n"
                                 "<:rp_utility1:371816529458626570> Personal Shield Devices are recharged to full capacity.\n"
                                 "Processing…\n"
                                 "Processing…\n"
                                 "Processing…\n"
                                 "<:rp_utility1:371816529458626570> Thermal Weaponry are recharged to full capacity.\n"
                                 "<:rp_utility1:371816529458626570> Massive Heat Surge Detected.\n"
                                 "Allow **5 minutes** for utility to cool for optimal performance.")
            embed.colour = discord.Colour.green()
        elif chance > 90:
            embed.description = ("Processing…\n"
                                 "Processing…\n"
                                 "<:rp_utility0:371816528326164490> Module Malfunction Detected.\n"
                                 "<:rp_utility0:371816528326164490> Personal Shield Devices failed to recharge.\n"
                                 "<:rp_utility0:371816528326164490> Thermal Weaponry failed to recharge.\n"
                                 "<:rp_utility1:371816529458626570> Massive Heat Surge Detected.\n"
                                 "<:rp_utility0:371816528326164490> Meltdown Detected.\n"
                                 "Allow **5 minutes** for utility to cool before triggering.")
            embed.colour = discord.Colour.red()
        else:
            embed.description = ("Processing…\n"
                                 "Processing…\n"
                                 "Processing…\n"
                                 "<:rp_utility1:371816529458626570> Personal Shield Devices are recharged to full capacity.\n"
                                 "Processing…\n"
                                 "Processing…\n"
                                 "Processing…\n"
                                 "<:rp_utility1:371816529458626570> hermal Weaponry are recharged to full capacity.\n"
                                 "<:rp_utility1:371816529458626570> Heat Surge Detected.\n"
                                 "Allow **60 seconds** for utility to cool for optimal performance.")
            embed.colour = discord.Colour.orange()
        await channel.send('', embed=embed)

    @_rp.command(name='afmu')
    async def _afmu(self, ctx, who=None, channel: discord.TextChannel = None):
        """
        Activates Auto Field Maintenance Unit
        """
        if not await can_manage_bot(ctx):
            who = None
            channel = None

        who = who or ctx.message.author
        channel = channel or ctx.channel

        chance = random.randint(1, 100)
        embed = discord.Embed(title="**::Auto Field Maintenance Unit::**")

        if isinstance(who, discord.Member):
            embed.set_author(name=who.nick or who.display_name, icon_url=who.avatar_url)
        else:
            embed.set_author(name=who)

        if chance <= 50:
            embed.description = ("Processing…\n"
                                 "Processing…\n"
                                 "Processing…\n"
                                 "<:rp_utility1:371816529458626570> Armor Integrity restored to 100%.\n"
                                 "Processing…\n"
                                 "Processing…\n"
                                 "Processing…\n"
                                 "<:rp_utility1:371816529458626570> Armor Modifier Integrity restored to 100%.\n"
                                 "Processing…\n"
                                 "Processing…\n"
                                 "Processing…\n"
                                 "<:rp_utility1:371816529458626570> Malfunctioned Accessories restored to 100%.\n"
                                 "Processing…\n"
                                 "Processing…\n"
                                 "<:rp_utility1:371816529458626570> Malfunctioned Utilities restored to 100%.\n"
                                 "<:rp_utility1:371816529458626570> Large Heat Surge Detected.\n"
                                 "<:rp_utility0:371816528326164490> Meltdown Detected.\n"
                                 "Allow **10 minutes** for utility to cool for optimal performance.")
            embed.colour = discord.Colour.green()
        elif chance > 75:
            embed.description = ("Processing…\n"
                                 "Processing…\n"
                                 "<:rp_utility0:371816528326164490> Module Malfunction Detected.\n"
                                 "<:rp_utility0:371816528326164490> Armor Integrity ignored by device.\n"
                                 "<:rp_utility0:371816528326164490> Armor Modifier Integrity ignored by device.\n"
                                 "<:rp_utility0:371816528326164490> Malfunctioned Accessories ignored by device.\n"
                                 "<:rp_utility0:371816528326164490> Malfunctioned Utilities ignored by device.\n"
                                 "<:rp_utility1:371816529458626570> Large Heat Surge Detected.\n"
                                 "<:rp_utility0:371816528326164490> Meltdown Detected.\n"
                                 "Allow **10 minutes** for utility to cool before triggering.")
            embed.colour = discord.Colour.red()
        else:
            embed.description = ("Processing…\n"
                                 "<:rp_utility0:371816528326164490> Armor Integrity ignored by device.\n"
                                 "Processing…\n"
                                 "<:rp_utility0:371816528326164490> Armor Modifier Integrity ignored by device.\n"
                                 "Processing…\n"
                                 "Processing…\n"
                                 "Processing…\n"
                                 "<:rp_utility1:371816529458626570> Malfunctioned Accessories restored to 100%.\n"
                                 "Processing…\n"
                                 "Processing…\n"
                                 "<:rp_utility1:371816529458626570> Malfunctioned Utilities restored to 100%.\n"
                                 "<:rp_utility1:371816529458626570> Large Heat Surge Detected.\n"
                                 "<:rp_utility0:371816528326164490> Meltdown Detected.\n"
                                 "Allow **10 minutes** for utility to cool for optimal performance.")
            embed.colour = discord.Colour.orange()
        await channel.send('', embed=embed)

    @_rp.command(name='chaff')
    async def _chaff(self, ctx, who=None, channel: discord.TextChannel = None):
        """
        Activates Chaff Launcher
        """
        if not await can_manage_bot(ctx):
            who = None
            channel = None

        who = who or ctx.message.author
        channel = channel or ctx.channel

        chance = random.randint(1, 100)
        embed = discord.Embed(title="**::Chaff Launcher::**")

        if isinstance(who, discord.Member):
            embed.set_author(name=who.nick or who.display_name, icon_url=who.avatar_url)
        else:
            embed.set_author(name=who)

        if chance <= 90:
            embed.description = ("<:rp_utility1:371816529458626570> Chaff launched successfully.\n"
                                 "<:rp_utility1:371816529458626570> Hostile Sensors are unable to track for 20 Seconds.\n"
                                 "<:rp_utility1:371816529458626570> Minor Heat Surge Detected.\n"
                                 "Allow **30 seconds** for utility to cool for optimal performance.")
            embed.colour = discord.Colour.green()
        else:
            embed.description = ("<:rp_utility0:371816528326164490> Module Malfunction Detected.\n"
                                 "<:rp_utility0:371816528326164490> Chaff failed to launch.\n"
                                 "<:rp_utility1:371816529458626570> Minor Heat Surge Detected.\n"
                                 "Allow **30 seconds** for utility to cool before triggering.")
            embed.colour = discord.Colour.red()
        await channel.send('', embed=embed)

    @_rp.command(name='els')
    async def _els(self, ctx, who=None, channel: discord.TextChannel = None):
        """
        Activates Environmental Layout Scanner
        """
        if not await can_manage_bot(ctx):
            who = None
            channel = None

        who = who or ctx.message.author
        channel = channel or ctx.channel

        chance = random.randint(1, 100)
        embed = discord.Embed(title="**::Environmental Layout Scanner::**")

        if isinstance(who, discord.Member):
            embed.set_author(name=who.nick or who.display_name, icon_url=who.avatar_url)
        else:
            embed.set_author(name=who)

        if chance <= 50:
            embed.description = ("Processing…\n"
                                 "Processing…\n"
                                 "Processing…\n"
                                 "<:rp_utility1:371816529458626570> Scan completed successfully.\n"
                                 "Processing…\n"
                                 "<:rp_utility1:371816529458626570> Landscape and structure layout updated.\n"
                                 "Processing…\n"
                                 "<:rp_utility1:371816529458626570> Data Package created, ready to download to a memory drive.\n"
                                 "<:rp_utility1:371816529458626570> Information updated to any detected Visual Assistant Systems in the squad.\n"
                                 "<:rp_utility1:371816529458626570> Heat Surge Detected.\n"
                                 "Allow **60 seconds** for utility to cool for optimal performance.")
            embed.colour = discord.Colour.green()
        elif chance > 90:
            embed.description = ("Processing…\n"
                                 "Processing…\n"
                                 "<:rp_utility0:371816528326164490> Module Malfunction Detected.\n"
                                 "<:rp_utility0:371816528326164490> Scan failed.\n"
                                 "<:rp_utility0:371816528326164490> Landscape and structure layout failed to update.\n"
                                 "Processing…\n"
                                 "Processing…\n"
                                 "<:rp_utility0:371816528326164490> Data Package failed, purging corrupted data.\n"
                                 "<:rp_utility1:371816529458626570> Heat Surge Detected.\n"
                                 "Allow **60 seconds** for utility to cool before triggering.")
            embed.colour = discord.Colour.red()
        else:
            embed.description = ("Processing…\n"
                                 "Processing…\n"
                                 "Processing…\n"
                                 "<:rp_utility1:371816529458626570> Scan completed successfully.\n"
                                 "Processing…\n"
                                 "<:rp_utility1:371816529458626570> Landscape and structure layout updated.\n"
                                 "Processing…\n"
                                 "Processing…\n"
                                 "<:rp_utility1:371816529458626570> Valuable insight on environment detected.\n"
                                 "Processing…\n"
                                 "<:rp_utility1:371816529458626570> Data Package created, ready to download to a memory drive.\n"
                                 "<:rp_utility1:371816529458626570> Information updated to any detected Visual Assistant Systems in the squad.\n"
                                 "<:rp_utility1:371816529458626570> Heat Surge Detected.\n"
                                 "Allow **60 seconds** for utility to cool for optimal performance.")
            embed.colour = discord.Colour.orange()
        await channel.send('', embed=embed)

    @_rp.command(name='hsl')
    async def _hsl(self, ctx, who=None, channel: discord.TextChannel = None):
        """
        Activates Heat Sink Launcher
        """
        if not await can_manage_bot(ctx):
            who = None
            channel = None

        who = who or ctx.message.author
        channel = channel or ctx.channel

        chance = random.randint(1, 100)
        embed = discord.Embed(title="**::Heat Sink Launcher::**")

        if isinstance(who, discord.Member):
            embed.set_author(name=who.nick or who.display_name, icon_url=who.avatar_url)
        else:
            embed.set_author(name=who)

        if chance <= 90:
            embed.description = ("Processing…\n"
                                 "Processing...\n"
                                 "<:rp_utility1:371816529458626570> All Generated Heat successfully pulled from Utilities.\n"
                                 "Processing…\n"
                                 "Processing…\n"
                                 "Processing...\n"
                                 "<:rp_utility1:371816529458626570> All Generated Heat successfully pulled from Thermal Weaponry.\n"
                                 "Processing…\n"
                                 "<:rp_utility1:371816529458626570> Heat Sink spin cycle initiated, preparing to launch.\n"
                                 "Processing…\n"
                                 "Processing…\n"
                                 "<:rp_utility1:371816529458626570> Heat Sink launched successfully.")
            embed.colour = discord.Colour.green()
        else:
            embed.description = ("Processing…\n"
                                 "Processing...\n"
                                 "<:rp_utility1:371816529458626570> All Generated Heat successfully pulled from Utilities.\n"
                                 "Processing…\n"
                                 "Processing…\n"
                                 "Processing...\n"
                                 "<:rp_utility1:371816529458626570> All Generated Heat successfully pulled from Thermal Weaponry.\n"
                                 "Processing…\n"
                                 "<:rp_utility1:371816529458626570> Heat Sink spin cycle initiated, preparing to launch.\n"
                                 "Processing…\n"
                                 "Processing…\n"
                                 "<:rp_utility0:371816528326164490> Heat buildup exceeds Heat Sink capacity.  Preparing to Overcharge disk.\n"
                                 "WARNING: Keep clear of Heat Sink when launched;\n"
                                 "<:rp_utility1:371816529458626570> Overcharged Heat Sink launched, certain to explode on contact.\n"
                                 "Utility ready for use.")
            embed.colour = discord.Colour.red()
        await channel.send('', embed=embed)

    @_rp.command(name='kws')
    async def _kws(self, ctx, who=None, channel: discord.TextChannel = None):
        """
        Activates Kill Warrant Scanner
        """
        if not await can_manage_bot(ctx):
            who = None
            channel = None

        who = who or ctx.message.author
        channel = channel or ctx.channel

        chance = random.randint(1, 100)
        embed = discord.Embed(title="**::Kill Warrant Scanner::**")

        if isinstance(who, discord.Member):
            embed.set_author(name=who.nick or who.display_name, icon_url=who.avatar_url)
        else:
            embed.set_author(name=who)

        if chance <= 90:
            embed.description = ("Processing…\n"
                                 "Processing…\n"
                                 "Processing…\n"
                                 "Processing…\n"
                                 "Processing…\n"
                                 "Processing...\n"
                                 "<:rp_utility1:371816529458626570> Identity Scan Completed.\n"
                                 "<:rp_utility1:371816529458626570> Information updated to any detected Visual Assistant Systems in the squad.\n"
                                 "<:rp_utility1:371816529458626570> Heat Surge Detected.\n"
                                 "Allow **30 seconds** for utility to cool for optimal performance.")
            embed.colour = discord.Colour.green()
        else:
            embed.description = ("Processing…\n"
                                 "Processing…\n"
                                 "Processing…\n"
                                 "<:rp_utility0:371816528326164490> Module Malfunction Detected.\n"
                                 "<:rp_utility1:371816529458626570> Identity Scan Failed.\n"
                                 "<:rp_utility1:371816529458626570> Heat Surge Detected.\n"
                                 "Allow **60 seconds** for utility to cool before triggering.")
            embed.colour = discord.Colour.red()
        await channel.send('', embed=embed)

    @_rp.command(name='hdp')
    async def _hdp(self, ctx, who=None, channel: discord.TextChannel = None):
        """
        Activates Holo-Me Decoy Projector
        """
        if not await can_manage_bot(ctx):
            who = None
            channel = None

        who = who or ctx.message.author
        channel = channel or ctx.channel

        chance = random.randint(1, 100)
        embed = discord.Embed(title="**::Holo-Me Decoy Projector::**")

        if isinstance(who, discord.Member):
            embed.set_author(name=who.nick or who.display_name, icon_url=who.avatar_url)
        else:
            embed.set_author(name=who)

        if chance <= 90:
            embed.description = ("<:rp_utility1:371816529458626570> 28 Decoy Clones projected successfully.\n"
                                 "<:rp_utility1:371816529458626570> Audio Shimmering transmitted successfully.\n"
                                 "<:rp_utility1:371816529458626570> Immune to targeting for 10 Seconds.\n"
                                 "<:rp_utility1:371816529458626570> Massive Heat Surge Detected.\n"
                                 "Allow **2 Minutes** for utility to cool for optimal performance.")
            embed.colour = discord.Colour.green()
        else:
            embed.description = ("Processing…\n"
                                 "Processing…\n"
                                 "<:rp_utility0:371816528326164490> Module Malfunction Detected.\n"
                                 "<:rp_utility0:371816528326164490> Decoy Clones failed to project.\n"
                                 "<:rp_utility0:371816528326164490> Audio Shimmering failed to transmit.\n"
                                 "<:rp_utility1:371816529458626570> Massive Heat Surge Detected.\n"
                                 "Allow **2 Minutes** for utility to cool before triggering.")
            embed.colour = discord.Colour.red()
        await channel.send('', embed=embed)

    @_rp.command(name='vdc')
    async def _vdc(self, ctx, who=None, channel: discord.TextChannel = None):
        """
        Activates Virtual Distortion Cloak
        """
        if not await can_manage_bot(ctx):
            who = None
            channel = None

        who = who or ctx.message.author
        channel = channel or ctx.channel

        chance = random.randint(1, 100)
        embed = discord.Embed(title="**::Virtual Distortion Cloak::**")

        if isinstance(who, discord.Member):
            embed.set_author(name=who.nick or who.display_name, icon_url=who.avatar_url)
        else:
            embed.set_author(name=who)

        if chance <= 90:
            embed.description = ("<:rp_utility1:371816529458626570> 60 Corrupted Holograms projected per minute.\n"
                                 "<:rp_utility1:371816529458626570> Generating disruptive audio successfully.\n"
                                 "<:rp_utility1:371816529458626570> Immune to recognition software for ten minutes.\n"
                                 "<:rp_utility1:371816529458626570> Massive Heat Surge Detected.\n"
                                 "Allow **2 Minutes** for utility to cool for optimal performance.")
            embed.colour = discord.Colour.green()
        else:
            embed.description = ("<:rp_utility0:371816528326164490> Module Malfunction Detected.\n"
                                 "<:rp_utility0:371816528326164490> 400 Corrupted Holograms erratically projected before jamming projector orb.\n"
                                 "<:rp_utility1:371816529458626570> Disrupted audio hauntingly transmitted before overloading system memory.\n"
                                 "<:rp_utility1:371816529458626570> Failed to conceal identity, drawing attention.\n"
                                 "<:rp_utility1:371816529458626570> Massive Heat Surge Detected.\n"
                                 "Allow **2 Minutes** for utility to cool before triggering.")
            embed.colour = discord.Colour.red()
        await channel.send('', embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(Roleplay(bot))


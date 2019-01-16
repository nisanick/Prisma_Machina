import asyncio
import random

import checks
from TextChecker import TextChecker
from database import Database
from checks import *
from data.rp_texts import *
from data.links import *
from web import Web
from roleplay.Player import Player

import discord
from discord.ext import commands


class Roleplay:
    def __init__(self, bot: commands.Bot):
        self.parameters = {}
        self.bot = bot
        self.delta = 10
        self.players = {}
        self.playerids = []
        self.announce_message = None
        self.system_message = None
        self.turn_number = 0
    
    @commands.group(name='rp', case_insensitive=True)
    async def _rp(self, ctx):
        """
        Base command for RP utilities. Use !help rp for details.
        Mind that parameters [who] [channel] are admin exclusive.
        """
        await ctx.message.delete()
        if ctx.invoked_subcommand is None:
            await ctx.send("Subcommand required!")
    
    @_rp.command(name='turn')
    @commands.check(checks.can_manage_rp)
    async def _turn(self, ctx):
        """
        Tells the bot to post used actions and start new turn.
        """
        message = '**::TURN {}::**\n'.format(self.turn_number)
        message += 'Turn ended with these actions taking place:\n'
        message += '```\n'
        message += "{:^35}|{:^25}\n".format('Player', 'Action')
        message += "{:*^35}|{:*^25}\n".format('', '')
        for player_id, (player, action) in self.players.items():
            player = self.system_message.guild.get_member(player_id)
            message += "{:<35}|{:<25}\n".format(player.nick or player.name, action or '<no action set>')
        message += '```\n'
        message += 'New turn has begun, please state your actions.'
        await self.bot.get_channel(326954112744816643).send(message)
        for player_id in self.playerids:
            player, action = self.players[player_id]
            self.players[player_id] = (player, None)
        self.turn_number += 1
        await self.post_players(True)
    
    @_rp.command(name='start')
    @commands.check(checks.can_manage_rp)
    async def _start(self, ctx):
        """
        Bot will create new RP session if there is not one running already.
        
        Players can join the session via `?rp join`
        Players are supposed to state their action with `?rp use` command each turn.
        Turns are ended by `?rp turn` command.
        Session is over when `?rp end` command is used.
        In case the session wasn't closed properly (bot crash, etc.) use `?rp clean` to reset it.
        """
        announce_channel = self.bot.get_channel(326954112744816643)
        system_channel = self.bot.get_channel(374691520055345162)
        db = await Database.get_connection(self.bot.loop)
        insert = "INSERT INTO roleplay_session(announce_id, system_id) values ($1, $2)"
        select = "SELECT 1 FROM roleplay_session WHERE done is FALSE"
        async with db.transaction():
            if await db.fetchval(select) is None:
                announce_message = await announce_channel.send("Session started. To participate, use `?rp join`")
                system_message = await system_channel.send("Session participants")
                self.announce_message = announce_message
                self.system_message = system_message
                self.turn_number = 1
                await db.execute(insert, *(str(announce_message.id), str(system_message.id)))
            else:
                await ctx.send('There is already an unfinished session. Please end it before starting new one.')
        await Database.close_connection(db)
    
    @_rp.command(name='join')
    async def _join(self, ctx):
        """
        Joins you to currently open session, if there is one at the moment.
        """
        player_id = ctx.author.id
        for player in self.playerids:
            if player == player_id:
                to_delete = await ctx.send('Player is already in session')
                await asyncio.sleep(1)
                await to_delete.delete()
                return
        args = {
            'discord_id': ctx.author.id
            # 'discord_id': '144229491907100672'
        }
        response = await Web.get_response(user_data_link, args)
        player = Player(player_id, response['Inventory'])
        self.players[player_id] = (player, None)
        self.playerids.append(player_id)
        await self.announce_message.edit(
            content='{}\n{} joined'.format(self.announce_message.content, ctx.author.nick or ctx.author.name))
        await self.post_players()
    
    async def post_players(self, new=False):
        if new:
            self.system_message = await self.bot.get_channel(374691520055345162).send('placeholder')
        message = '```\n'
        message += "{:^35}|{:^25}\n".format('Player', 'Action')
        message += "{:*^35}|{:*^25}\n".format('', '')
        for player_id, (player, action) in self.players.items():
            player = self.system_message.guild.get_member(player_id)
            message += "{:<35}|{:<25}\n".format(player.nick or player.name, action or '<no action set>')
        message += '```'
        await self.system_message.edit(content=message)
    
    @_rp.command(name='use')
    async def _use(self, ctx, *, what=None):
        """
        Queues action for you this turn, refer to ?help rp use
        
        Options for 'what' are:
        number 1-6 for equiped items in order of the character list.
        1 - Light
        2 - Medium
        3 - Heavy
        4 - Melee
        5 - Defense
        6 - Consumable !!IMPORTANT - will consume your item on use
        
        To use equiped utility slots, use abbreviate form of the name:
        Chaff launcher               -> chaff
        Auto Field Maintenance Unit  -> afmu
        Environmental Layout Scanner -> els
        Heat Sink Launcher           -> hsl
        Kill Warrant Scanner         -> kws
        Shield Cell Bank             -> scb
        Encryption Cracking Unit     -> ecu
        Holo-Me Decoy Projector      -> hdp
        Virtual Distortion Cloak     -> vdc
        Electronic Ghost Generator   -> egg
        
        Last option is 'hack' which will use your equiped hack tool
        """
        
        if what is None:
            return
        
        if ctx.author.id in self.playerids and self.players[ctx.author.id][1] is None:
            player, action = self.players[ctx.author.id]
            
            if what == '1':
                action = player.light[1] if player.light else None
            elif what == '2':
                action = player.medium[1] if player.medium else None
            elif what == '3':
                action = player.heavy[1] if player.heavy else None
            elif what == '4':
                action = player.melee[1] if player.melee else 'Punch'
            elif what == '5':
                action = player.defense[1] if player.defense else None
            elif what == '6':
                action = player.disposable[1] if player.disposable else None
                if action:
                    await player.use_item()
            elif what == 'hack':
                if player.gloves[1].lower().__contains__("hacking") and player.gloves[1].lower().__contains__("system"):
                    action = await self._hack(ctx)
                    if not action:
                        return
            elif player.have_util(what):
                action = what
                await getattr(self, '_' + action)(ctx)
            self.players[ctx.author.id] = (player, action)
            if action is None:
                to_delete = await ctx.send("You don't own a tool required to do this action")
                await asyncio.sleep(2)
                await to_delete.delete()
            else:
                to_delete = await ctx.send("Action registered.")
                await asyncio.sleep(2)
                await to_delete.delete()
            await self.post_players()
    
    @_rp.command(name='pass')
    async def _pass(self, ctx):
        if ctx.author.id in self.playerids and self.players[ctx.author.id][1] is None:
            player, action = self.players[ctx.author.id]
            action = 'pass'
            self.players[ctx.author.id] = (player, action)
            to_delete = await ctx.send("Action registered.")
            await asyncio.sleep(2)
            await to_delete.delete()
    
    @_rp.command(name='end')
    @commands.check(checks.can_manage_rp)
    async def _end(self, ctx):
        """
        Ends currently open rp session
        """
        db = await Database.get_connection(self.bot.loop)
        probe = "SELECT 1 FROM roleplay_session WHERE done IS FALSE"
        select = "SELECT session_id, announce_id, system_id FROM roleplay_session WHERE done = FALSE"
        update = "UPDATE roleplay_session SET done = TRUE WHERE session_id = $1"
        async with db.transaction():
            if await db.fetchval(probe) is None:
                to_delete = await ctx.send("There is no open session to close.")
                await asyncio.sleep(2)
                await to_delete.delete()
            else:
                async for (session_id, announce_id, system_id) in db.cursor(select):
                    sys_message = await self.bot.get_channel(374691520055345162).get_message(int(system_id))
                    self.players.clear()
                    self.playerids = []
                    self.announce_message = None
                    self.system_message = None
                    await db.execute(update, session_id)
                    await self.bot.get_channel(326954112744816643).send('Session ended. Thanks for participating')
                    await sys_message.edit(content='{}\nSession ended'.format(sys_message.content))
        await Database.close_connection(db)
    
    @_rp.command(name='tool')
    @commands.check(checks.can_manage_rp)
    async def _tool(self, ctx, what, who, channel: discord.TextChannel):
        """
        Used in place of old RP utility commands
        """
        try:
            await getattr(self, '_' + what)(ctx, who, channel)
        except AttributeError:
            await ctx.send("tool {} doesn't exist".format(what))
    
    @_rp.command(name='clean')
    @commands.check(checks.can_manage_rp)
    async def _clean(self, ctx):
        """
        Force-closes all RP sessions
        """
        db = await Database.get_connection(self.bot.loop)
        update = "UPDATE roleplay_session SET done = TRUE WHERE done IS FALSE"
        async with db.transaction():
            await db.execute(update)
            self.players.clear()
            self.playerids = []
            self.announce_message = None
            self.system_message = None
            await ctx.send('Sessions cleaned')
        await Database.close_connection(db)
    
    @_rp.command(name='set')
    @commands.check(checks.can_manage_rp)
    async def _set(self, ctx, what: str, *params):
        """
        Helper command to set various parameters to RP session.

        Currenly can be used only to set hacking target, for example `?rp set target 3` to set hack target to 3
        """
        if what == 'target' and params[0] is not None:
            self.parameters[what] = params[0]
        elif what == 'channel' and params[0] is not None:
            self.parameters[what] = params[0]
        
        else:
            to_delete = await ctx.send('Unknown parameter!')
            await asyncio.sleep(2)
            await to_delete.delete()
    
    async def _hack(self, ctx, difficulty: int = None, who=None, channel: discord.TextChannel = None):
        """
        Initiates hack with specified difficulty.
        """
        if difficulty is None and 'target' in self.parameters and self.parameters['target'] is not None:
            difficulty = int(self.parameters['target'])
        else:
            to_delete = await ctx.send("There is no hack target specified")
            await asyncio.sleep(1)
            await to_delete.delete()
            values = self.players[ctx.author.id]
            self.players[ctx.author.id] = (values[0], None)
            await self.post_players()
            return None
        
        if not await can_manage_bot(ctx):
            who = None
            channel = None
            difficulty = abs(difficulty)
        
        if difficulty > 0:
            limit = [
                10, 25, 40, 50, 70, 75,
            ]
        else:
            limit = [
                -1, -1, -1, -1, -1, -1,
            ]
        
        who = who or ctx.message.author
        channel = channel or ctx.channel
        
        embed = discord.Embed(title="**::Hacking sequence initiated for Security Level {}::**".format(abs(difficulty)),
                              description=(
                                  "<:rp_utility1:371816529458626570> Encryption Cracking Unit paired with device.\n"
                                  "<:rp_utility1:371816529458626570> Emulation Program Functional.\n"
                                  "<:rp_utility1:371816529458626570> Data Package Compilation Program Functional.\n"
                                  "<:rp_utility1:371816529458626570> Virus Defense Program Functional."),
                              colour=discord.Colour.orange())
        if isinstance(who, discord.Member):
            embed.set_author(name=who.nick or who.display_name, icon_url=who.avatar_url)
        else:
            if who is not None:
                embed.set_author(name=who)
            else:
                embed.set_author(name='Unknown user')
        message = await channel.send('', embed=embed)
        await asyncio.sleep(self.delta)
        
        for i in range(abs(difficulty)):
            if i > 0:
                embed.remove_field(0)
                await asyncio.sleep(self.delta)
            
            prob = random.randint(0, 100)
            
            if prob > limit[i]:
                embed.add_field(name="**[Core Process {} of {}]**".format(i + 1, abs(difficulty)),
                                value=hacks_pass[i].format(embed.author.name), inline=False)
                await message.edit(embed=embed)
            else:
                embed.add_field(name="**[Core Process {} of {}]**".format(i + 1, abs(difficulty)),
                                value=hacks_fail[i].format(embed.author.name), inline=False)
                await message.edit(embed=embed)
                await asyncio.sleep(self.delta)
                embed.colour = discord.Colour.red()
                embed.add_field(name="**::Hacking sequence failed::**",
                                value=(
                                    "<:rp_utility0:371816528326164490> Encryption Cracking Unit disconnected from device.\n"
                                    "<:rp_utility0:371816528326164490> Emulation Program was locked out of the system.\n"
                                    "<:rp_utility0:371816528326164490> Data Package Failed, purging corrupted data.\n"
                                    "<:rp_utility1:371816529458626570> All hostile viruses quarantined and purged.\n"
                                    "<:rp_utility1:371816529458626570> Heat Surge Detected.\n"
                                    "Allow **30 seconds** for utility to cool for optimal performance."))
                await message.edit(embed=embed)
                return 'hack'
        
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
        return 'hack'
    
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
            embed.description = TextChecker.replace_emotes("Processing…\n"
                                                           "Processing…\n"
                                                           "Processing…\n"
                                                           "<:rp_utility1:371816529458626570> Personal Shield Devices are recharged to full capacity.\n"
                                                           "Processing…\n"
                                                           "Processing…\n"
                                                           "Processing…\n"
                                                           "<:rp_utility1:371816529458626570> Thermal Weaponry are recharged to full capacity.\n"
                                                           "<:rp_utility1:371816529458626570> Massive Heat Surge Detected.\n"
                                                           "Allow **5 minutes** for utility to cool for optimal performance.",
                                                           self.bot)
            embed.colour = discord.Colour.green()
        elif chance > 90:
            embed.description = TextChecker.replace_emotes("Processing…\n"
                                                           "Processing…\n"
                                                           "<:rp_utility0:371816528326164490> Module Malfunction Detected.\n"
                                                           "<:rp_utility0:371816528326164490> Personal Shield Devices failed to recharge.\n"
                                                           "<:rp_utility0:371816528326164490> Thermal Weaponry failed to recharge.\n"
                                                           "<:rp_utility1:371816529458626570> Massive Heat Surge Detected.\n"
                                                           "<:rp_utility0:371816528326164490> Meltdown Detected.\n"
                                                           "Allow **5 minutes** for utility to cool before triggering.",
                                                           self.bot)
            embed.colour = discord.Colour.red()
        else:
            embed.description = TextChecker.replace_emotes("Processing…\n"
                                                           "Processing…\n"
                                                           "Processing…\n"
                                                           ":rp_utility1: Personal Shield Devices are recharged to full capacity.\n"
                                                           "Processing…\n"
                                                           "Processing…\n"
                                                           "Processing…\n"
                                                           ":rp_utility1: hermal Weaponry are recharged to full capacity.\n"
                                                           ":rp_utility1: Heat Surge Detected.\n"
                                                           "Allow **60 seconds** for utility to cool for optimal performance.",
                                                           self.bot)
            embed.colour = discord.Colour.orange()
        await channel.send('', embed=embed)
    
    async def _afmu(self, ctx, who=None, channel: discord.TextChannel = None):
        """
        Activates Auto Field Maintenance Unit.
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
    
    async def _chaff(self, ctx, who=None, channel: discord.TextChannel = None):
        """
        Activates Chaff Launcher.
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
    
    async def _els(self, ctx, who=None, channel: discord.TextChannel = None):
        """
        Activates Environmental Layout Scanner.
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
    
    async def _ecu(self, ctx, who=None, channel: discord.TextChannel = None):
        """
        Activates Encryption Cracking Unit.
        """
        if not await can_manage_bot(ctx):
            who = None
            channel = None
        
        who = who or ctx.message.author
        channel = channel or ctx.channel
        
        chance = random.randint(1, 100)
        embed = discord.Embed(title="**::Encryption Cracking Unit::**")
        
        if isinstance(who, discord.Member):
            embed.set_author(name=who.nick or who.display_name, icon_url=who.avatar_url)
        else:
            embed.set_author(name=who)
        
        if chance <= 50:
            embed.description = ("<:rp_utility1:371816529458626570> Detected encrypted data deciphered.\n"
                                 "<:rp_utility1:371816529458626570> Any communications chatter intercepted.\n"
                                 "<:rp_utility1:371816529458626570> Hostile Viruses Purged.\n"
                                 "Processing…\n"
                                 "Processing…\n"
                                 "<:rp_utility1:371816529458626570> All deciphered data stored on memory device.\n"
                                 "<:rp_utility1:371816529458626570> Heat Surge Detected.\n"
                                 "Allow **2 Minutes** for utility to cool for optimal performance.")
            embed.colour = discord.Colour.green()
        elif chance > 80:
            embed.description = ("Processing…\n"
                                 "Processing…\n"
                                 "Processing…\n"
                                 "<:rp_utility0:371816528326164490> Module Malfunction Detected\n"
                                 "Processing…\n"
                                 "<:rp_utility0:371816528326164490> The device has failed to respond.\n"
                                 "Processing…\n"
                                 "<:rp_utility1:371816529458626570> Massive Heat Surge Detected.\n"
                                 "Allow **2 Minutes** for utility to cool for optimal performance.")
            embed.colour = discord.Colour.red()
        else:
            embed.description = ("<:rp_utility1:371816529458626570> Detected encrypted data deciphered.\n"
                                 "Processing…\n"
                                 "<:rp_utility0:371816528326164490> Failed to intercept communications chatter.\n"
                                 "<:rp_utility1:371816529458626570> Hostile Viruses Purged.\n"
                                 "Processing…\n"
                                 "Processing…\n"
                                 "<:rp_utility1:371816529458626570> All deciphered data stored on memory device.\n"
                                 "<:rp_utility1:371816529458626570> Heat Surge Detected.\n"
                                 "Allow **2 Minutes** for utility to cool for optimal performance.")
            embed.colour = discord.Colour.orange()
        await channel.send('', embed=embed)
    
    async def _hsl(self, ctx, who=None, channel: discord.TextChannel = None):
        """
        Activates Heat Sink Launcher.
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
    
    async def _kws(self, ctx, who=None, channel: discord.TextChannel = None):
        """
        Activates Kill Warrant Scanner.
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
    
    async def _egg(self, ctx, who=None, channel: discord.TextChannel = None):
        """
        Activates Electronic Ghost Generator.
        """
        if not await can_manage_bot(ctx):
            who = None
            channel = None
        
        who = who or ctx.message.author
        channel = channel or ctx.channel
        
        chance = random.randint(1, 100)
        embed = discord.Embed(title="**::Electronic Ghost Generator::**")
        
        if isinstance(who, discord.Member):
            embed.set_author(name=who.nick or who.display_name, icon_url=who.avatar_url)
        else:
            embed.set_author(name=who)
        
        if chance <= 90:
            embed.description = ("<:rp_utility1:371816529458626570> Frequencies generated successfully.\n"
                                 "<:rp_utility1:371816529458626570> Effective range is **100 Meters**.\n"
                                 "<:rp_utility1:371816529458626570> All individuals within 100 Meters are delirious and will experience hallucinations.\n"
                                 "<:rp_utility1:371816529458626570>  Massive Heat Surge Detected.\n"
                                 "Allow **2 Minutes** for utility to cool for optimal performance.\n"
                                 )
            embed.colour = discord.Colour.green()
        else:
            embed.description = (":rp_utility1: Frequencies generated successfully.\n"
                                 "Processing…\n"
                                 "Processing…\n"
                                 "<:rp_utility0:371816528326164490> Module Malfunction Detected\n"
                                 "Processing…\n"
                                 "<:rp_utility0:371816528326164490> Effective range is **5 Meters**.\n"
                                 "<:rp_utility1:371816529458626570> " + (
                                         who.nick or who.display_name) + " is delirious and will experience hallucinations.\n"
                                                                         "<:rp_utility1:371816529458626570> Massive Heat Surge Detected.\n"
                                                                         "Allow **2 Minutes** for utility to cool for optimal performance.\n")
            embed.colour = discord.Colour.red()
        await channel.send('', embed=embed)
    
    async def _hdp(self, ctx, who=None, channel: discord.TextChannel = None):
        """
        Activates Holo-Me Decoy Projector.
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
    
    async def _vdc(self, ctx, who=None, channel: discord.TextChannel = None):
        """
        Activates Virtual Distortion Cloak.
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

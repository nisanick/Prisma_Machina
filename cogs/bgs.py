from datetime import datetime

import discord
from discord.ext import commands
import asyncio

import checks
import database
from dateutil.parser import isoparse

from config import BGS_CHANNEL
from data.faction import Faction
from web import Web


class BGS(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.system_cache = {}
        self.faction_cache = {}
        self.updated_systems = set()
        self.last_tick = None
        self.tick_id = 0
        self.faction_data = {
            75253: Faction(75253, "Colonists of Aurora", "https://inara.cz/minorfaction/44432/"),
            23831: Faction(23831, "Prismatic Imperium", "https://inara.cz/minorfaction/25441/"),
            74847: Faction(74847, "Adamantine Union", "https://inara.cz/minorfaction/35809/")
        }
        self.war_cache = {}
        
    # @commands.command(name='fullscan', case_insensitive=True, hidden=True)
    # @commands.check(checks.can_manage_bot)
    async def _full_scan(self, ctx, *, faction_name):
        async with ctx.typing():
            await self._fullscan_faction(faction_name, 1)
        await ctx.send("done")
        
    async def _fullscan_faction(self, faction_name, page):
        args = {
            'factionname': faction_name,
            'page': page
        }
        
        data = await Web.get_response('https://eddbapi.kodeblox.com/api/v4/populatedsystems', args, 'object')

        db = await database.Database.get_connection(self.bot.loop)
        async with db.transaction():
    
            tick_select = "SELECT id as tick_id, time FROM tick ORDER BY time DESC LIMIT 1"
            self.tick_id = (await db.fetchrow(tick_select))['tick_id']
            
            for system in data.docs:
                if str(system.id) not in self.system_cache:
                    self.system_cache[str(system.id)] = system.name
                insert_system = "INSERT INTO star_system VALUES ($1, $2, $3, $4 , $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15) ON CONFLICT DO NOTHING "
                if str(system.controlling_minor_faction_id) in self.faction_cache:
                    controling_faction_name = self.faction_cache[str(system.controlling_minor_faction_id)]
                else:
                    controling_faction_data = await Web.get_response('https://eddbapi.kodeblox.com/api/v4/factions', {'eddbid': system.controlling_minor_faction_id}, 'object')
                    controling_faction_name = controling_faction_data.docs[0].name
                    self.faction_cache[str(system.controlling_minor_faction_id)] = controling_faction_name
                our_faction = 0
                for faction in system.minor_faction_presences:
                    if faction.minor_faction_id in self.faction_data:
                        our_faction = faction.minor_faction_id
                system_values = (
                    system.id,
                    system.name,
                    system.x,
                    system.y,
                    system.z,
                    controling_faction_name,
                    system.needs_permit,
                    system.power,
                    system.power_state,
                    system.reserve_type,
                    system.primary_economy,
                    system.security,
                    system.population,
                    system.edsm_id,
                    our_faction
                )
            
                await db.execute(insert_system, *system_values)
                for faction in system.minor_faction_presences:
                    await self._process_faction_data(faction.minor_faction_id)
                
                    states = ""
                    pending = ""
                    recovering = ""
                    for state in faction.active_states:
                        if len(states) > 0:
                            states = states + '|'
                        states = states + state.name
                        
                    for state in faction.pending_states:
                        if len(pending) > 0:
                            pending = pending + '|'
                        pending = pending + state.name

                    for state in faction.recovering_states:
                        if len(recovering) > 0:
                            recovering = recovering + '|'
                        recovering = recovering + state.name
                        
                    async with db.transaction():
                        insert_influence = "INSERT INTO influence(faction, system, influence, tick, states, pending, recovering) VALUES($1, $2, $3, $4, $5, $6, $7) ON CONFLICT DO NOTHING"
                        influence_values = (
                            faction.minor_faction_id,
                            system.id,
                            faction.influence,
                            self.tick_id,
                            states,
                            pending,
                            recovering
                        )
                        await db.execute(insert_influence, *influence_values)
        await database.Database.close_connection(db)
        
        if int(data.page) < int(data.pages):
            await self._fullscan_faction(faction_name, page + 1)

    async def _process_faction_data(self, faction_id):
        args = {
            'eddbid': faction_id
        }
        data = await Web.get_response('https://eddbapi.kodeblox.com/api/v4/factions', args, 'object')
    
        db = await database.Database.get_connection(self.bot.loop)
        async with db.transaction():
            for faction in data.docs:
                if str(faction_id) not in self.faction_cache:
                    self.faction_cache[str(faction.id)] = faction.name
                insert_faction = "INSERT INTO faction VALUES ($1, $2, $3, $4, $5, $6) ON CONFLICT DO NOTHING "
                
                if faction.home_system_id is not None:
                    if str(faction.home_system_id) in self.system_cache:
                        system_name = self.system_cache[str(faction.home_system_id)]
                    else:
                        home_system_data = await Web.get_response('https://eddbapi.kodeblox.com/api/v4/populatedsystems', {'eddbid': faction.home_system_id}, 'object')
                        system_name = home_system_data.docs[0].name
                        self.system_cache[str(faction.home_system_id)] = system_name
                else:
                    system_name = ""
                faction_values = (
                    faction.id,
                    faction.name,
                    faction.is_player_faction,
                    system_name,
                    faction.allegiance,
                    faction.government
                )
            
                await db.execute(insert_faction, *faction_values)
        await database.Database.close_connection(db)
        
    async def _get_system_id(self, system_name):
        db = await database.Database.get_connection(self.bot.loop)
        async with db.transaction():
            system_result = await db.fetchrow("SELECT id FROM star_system where name = $1", system_name)
            if system_result is None:
                home_system_data = await Web.get_response('https://eddbapi.kodeblox.com/api/v4/populatedsystems',
                                                          {'name': system_name}, 'object')
                for system in home_system_data.docs:
                    if str(system.id) not in self.system_cache:
                        self.system_cache[str(system.id)] = system.name
                    insert_system = "INSERT INTO star_system VALUES ($1, $2, $3, $4 , $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15) ON CONFLICT DO NOTHING "
                    if str(system.controlling_minor_faction_id) in self.faction_cache:
                        controling_faction_name = self.faction_cache[str(system.controlling_minor_faction_id)]
                    else:
                        controling_faction_data = await Web.get_response('https://eddbapi.kodeblox.com/api/v4/factions',
                                                                         {'eddbid': system.controlling_minor_faction_id},
                                                                         'object')
                        controling_faction_name = controling_faction_data.docs[0].name
                        self.faction_cache[str(system.controlling_minor_faction_id)] = controling_faction_name
                    our_faction = 0
                    for faction in system.minor_faction_presences:
                        if faction.minor_faction_id in self.faction_data:
                            our_faction = faction.minor_faction_id
                        
                    system_values = (
                        system.id,
                        system.name,
                        system.x,
                        system.y,
                        system.z,
                        controling_faction_name,
                        system.needs_permit,
                        system.power,
                        system.power_state,
                        system.reserve_type,
                        system.primary_economy,
                        system.security,
                        system.population,
                        system.edsm_id,
                        our_faction
                    )
                    system_id = system.id
    
                    await db.execute(insert_system, *system_values)
            else:
                system_id = system_result['id']

        await database.Database.close_connection(db)
        return system_id
    
    async def _get_faction_id(self, faction_name):
        db = await database.Database.get_connection(self.bot.loop)
        async with db.transaction():
            faction_result = await db.fetchrow("SELECT id FROM faction where name = $1", faction_name)
            if faction_result is None:
                faction_data = await Web.get_response('https://eddbapi.kodeblox.com/api/v4/factions',
                                                          {'name': faction_name}, 'object')
                for faction in faction_data.docs:
                    if str(faction.id) not in self.faction_cache:
                        self.faction_cache[str(faction.id)] = faction.name
                    insert_faction = "INSERT INTO faction VALUES ($1, $2, $3, $4, $5, $6) ON CONFLICT DO NOTHING "
    
                    if faction.home_system_id is not None:
                        if str(faction.home_system_id) in self.system_cache:
                            system_name = self.system_cache[str(faction.home_system_id)]
                        else:
                            faction_data = await Web.get_response(
                                'https://eddbapi.kodeblox.com/api/v4/populatedsystems',
                                {'eddbid': faction.home_system_id}, 'object')
                            system_name = faction_data.docs[0].name
                            self.system_cache[str(faction.home_system_id)] = system_name
                    else:
                        system_name = ""
                    faction_values = (
                        faction.id,
                        faction.name,
                        faction.is_player_faction,
                        system_name,
                        faction.allegiance,
                        faction.government
                    )
                    faction_id = faction.id
    
                    await db.execute(insert_faction, *faction_values)
            else:
                faction_id = faction_result['id']
    
        await database.Database.close_connection(db)
        return faction_id

    async def set_tick_date(self, date):
        db = await database.Database.get_connection(self.bot.loop)
        async with db.transaction():
            if self.last_tick is None or self.last_tick < date:
                insert_tick = "INSERT INTO tick(time) values($1) ON CONFLICT DO NOTHING"
                await db.execute(insert_tick, date)
                self.updated_systems = set()
                self.war_cache = {}
                self.faction_data = {
                    75253: Faction(75253, "Colonists of Aurora", "https://inara.cz/minorfaction/44432/"),
                    23831: Faction(23831, "Prismatic Imperium", "https://inara.cz/minorfaction/25441/"),
                    74847: Faction(74847, "Adamantine Union", "https://inara.cz/minorfaction/35809/")
                }
                self.last_tick = date
                tick_select = "SELECT id as tick_id, time FROM tick ORDER BY time DESC LIMIT 1"
                self.tick_id = (await db.fetchrow(tick_select))['tick_id']
                channel = self.bot.get_channel(BGS_CHANNEL)
                # await self.recheck_systems() FIXME - EDDN API is currently not updating
                self.faction_data[75253].message = await self.setup_bgs_message(channel, 75253)  # Colonists of Aurora
                self.faction_data[23831].message = await self.setup_bgs_message(channel, 23831)  # Prismatic Imperium
                self.faction_data[74847].message = await self.setup_bgs_message(channel, 74847)  # Adamantine Union
                update_faction = "UPDATE faction SET message_id = $1 WHERE id = $2"
                await db.execute(update_faction, *(self.faction_data[75253].message, 75253))
                await db.execute(update_faction, *(self.faction_data[23831].message, 23831))
                await db.execute(update_faction, *(self.faction_data[74847].message, 74847))
            
        await database.Database.close_connection(db)
        
    async def setup_bgs_message(self, channel, faction_id):
        
        embed = discord.Embed(colour=discord.Colour(0x992d22), url=self.faction_data[faction_id].link, title=self.faction_data[faction_id].name.upper())
        embed.set_author(name="Tick at {:%d %b %Y %H:%M}".format(self.last_tick))
        db = await database.Database.get_connection(self.bot.loop)
        async with db.transaction():
            system_select = "select id as system_id, name from star_system where our_faction_id = $1 order by name"
            system_count = 0
            systems = []
            async for (system_id, name) in db.cursor(system_select, faction_id):
                system_count = system_count + 1
                systems.append(name)
            self.faction_data[faction_id].systems = system_count
            # progress field
            embed.add_field(name="Tour progress", value="0/{} - 0%".format(system_count), inline=False)
            
            # missing stations
            if len(systems) > 0:
                missing_systems = ", ".join(systems)
            else:
                missing_systems = "Tour completed"
            embed.add_field(name="Missing systems", value="{}".format(missing_systems), inline=False)
            
            # states
            embed.add_field(name="Active states", value="None", inline=False)
            embed.add_field(name="Pending states", value="None")
            embed.add_field(name="Recovering states", value="None")

            # expansion warning
            embed.add_field(name="Expansion warning", value="None")
            
            # low inf warning
            embed.add_field(name="Inf getting low", value="None")
            
            # conflict warning
            embed.add_field(name="Inf too low", value="None")

            # Not controll system warning
            embed.add_field(name="Not in control", value="None")
            
            
        await database.Database.close_connection(db)
        message = await channel.send(embed=embed)
        # await message.pin()
        return message.id
    
    async def recheck_systems(self):
        db = await database.Database.get_connection(self.bot.loop)
        async with db.transaction():
            system_select = "SELECT id as system_id, our_faction_id FROM star_system WHERE our_faction_id > 0"
            async for (system_id, our_faction_id) in db.cursor(system_select):
                system_data = await Web.get_response('https://eddbapi.kodeblox.com/api/v4/populatedsystems',
                                                     {'eddbid': system_id}, 'object')
                present = False
                for system in system_data.docs:
                    for faction in system.minor_faction_presences:
                        if faction.minor_faction_id == our_faction_id:
                            present = True
                if not present:
                    remove_query = "DELETE FROM star_system WHERE id = $1"
                    await db.execute(remove_query, system_id)
        await database.Database.close_connection(db)
        
    async def init_bgs(self):
        db = await database.Database.get_connection(self.bot.loop)
        async with db.transaction():
            tick_select = "SELECT id as tick_id, time FROM tick ORDER BY time DESC LIMIT 1"
            tick_id, time = await db.fetchrow(tick_select)
            self.tick_id = tick_id
            self.last_tick = time

            messages_select = "SELECT id as faction_id, message_id FROM faction where id in (74847, 23831, 75253)"
            async for (faction_id, message_id) in db.cursor(messages_select):
                system_select = "select count(*) as system_count from star_system where our_faction_id = $1"
                async for record in db.cursor(system_select, faction_id):
                    self.faction_data[faction_id].systems = record['system_count']
                self.faction_data[faction_id].message = message_id
                states_select = "select star_system.name, influence.system, influence.influence, influence.states, pending, recovering from influence join star_system on star_system.id = influence.system where tick = $1 and faction = $2"
                async for (name, system_id, influence, states, pending, recovering) in db.cursor(states_select, *(tick_id, faction_id)):
                    self.updated_systems.add(name)
                    self.faction_data[faction_id].set_active(states)
                    self.faction_data[faction_id].set_pending(pending)
                    self.faction_data[faction_id].set_recovering(recovering)
                    influence_select = "select faction, influence.influence from influence where influence.system = $1 and tick = $2 order by influence desc limit 2"
                    their_influence = 0
                    async for (inf_faction_id, faction_influence) in db.cursor(influence_select, *(system_id, tick_id)):
                        if not inf_faction_id == faction_id:
                            if faction_influence > their_influence:
                                their_influence = faction_influence
                    if influence > 65.00:
                        self.faction_data[faction_id].expansion_warning.append("{} {}%".format(name, round(influence, 2)))
                    else:
                        difference = influence - their_influence
                        if 10.00 < difference <= 20.00:
                            self.faction_data[faction_id].mild_warning.append(
                                "{} {}% ({})".format(name, round(influence, 2), round(difference, 2)))
                        elif difference < 0.00:
                            self.faction_data[faction_id].not_control.append(
                                "{} {}% ({})".format(name, round(influence, 2), round(difference, 2)))
                        elif difference <= 10.00:
                            self.faction_data[faction_id].high_warning.append(
                                "{} {}% ({})".format(name, round(influence, 2), round(difference, 2)))
                await self.update_message(faction_id)
            
        await database.Database.close_connection(db)

    async def update_message(self, faction_id, conflict_data=None):
        faction = self.faction_data[faction_id]
        channel = self.bot.get_channel(BGS_CHANNEL)
        message = await channel.fetch_message(faction.message)
        embed = message.embeds[0]
        db = await database.Database.get_connection(self.bot.loop)
        async with db.transaction():
            system_select = "select star_system.id as system_id, name from star_system" \
                            " left join influence on star_system.id = influence.system and tick = $1 " \
                            "where our_faction_id = $2 and influence.influence is null order by name;"
            missing_count = 0
            missing_systems = []
            async for (system_id, name) in db.cursor(system_select, *(self.tick_id, faction_id)):
                missing_count = missing_count + 1
                missing_systems.append(name)
            done_count = faction.systems - missing_count
            percentage = 100 * done_count / faction.systems
            embed.set_field_at(0, name="Tour progress", value="{}/{} - {}%".format(done_count, faction.systems, round(percentage)), inline=False)
            
            if len(missing_systems) > 0:
                systems = ", ".join(missing_systems)
            else:
                systems = "Tour completed"
            embed.set_field_at(1, name="Missing systems", value="{}".format(systems), inline=False)
            
            embed.set_field_at(2, name="Active states", value="{}".format(faction.active), inline=False)
            embed.set_field_at(3, name="Pending states", value="{}".format(faction.pending))
            embed.set_field_at(4, name="Recovering states", value="{}".format(faction.recovering))

            if len(faction.expansion_warning) > 0:
                expansion_warning = "\n".join(faction.expansion_warning)
            else:
                expansion_warning = "None"
                
            if len(faction.mild_warning) > 0:
                mild_warning = "\n".join(faction.mild_warning)
            else:
                mild_warning = "None"
                
            if len(faction.high_warning) > 0:
                high_warning = "\n".join(faction.high_warning)
            else:
                high_warning = "None"
                
            if len(faction.not_control) > 0:
                not_control = "\n".join(faction.not_control)
            else:
                not_control = "None"

            embed.set_field_at(5, name="Expansion warning", value="{}".format(expansion_warning))
            embed.set_field_at(6, name="Inf getting low", value="{}".format(mild_warning))
            embed.set_field_at(7, name="Inf too low", value="{}".format(high_warning))
            embed.set_field_at(8, name="Not in control", value="{}".format(not_control))
            
            if conflict_data is not None:
                name, value = conflict_data
                embed.add_field(name=name, value=value)
            
            await message.edit(embed=embed)
            
        await database.Database.close_connection(db)
        
    async def submit(self, data):
        db = await database.Database.get_connection(self.bot.loop)

        influences = []
        our_influence = 0
        our_id = 0
        skip = False
        conflict_data = None
        async with db.transaction():
            timestamp = isoparse(data.timestamp)
            # if timestamp > self.last_tick and data.StarSystem not in self.updated_systems:
            if timestamp > self.last_tick:
                if data.StarSystem not in self.updated_systems:
                    self.updated_systems.add(data.StarSystem)
                system_id = await self._get_system_id(data.StarSystem)
                
                for faction in data.Factions:
                    faction_id = await self._get_faction_id(faction.Name)
                    
                    states = ""
                    pending = ""
                    recovering = ""
                    
                    try:
                        for state in faction.ActiveStates:
                            if len(states) > 0:
                                states = states + '|'
                            states = states + state.State
                    except AttributeError as e:
                        states = faction.FactionState
                        
                    try:
                        for state in faction.RecoveringStates:
                            if len(recovering) > 0:
                                recovering = recovering + '|'
                            recovering = recovering + state.State
                    except AttributeError as e:
                        recovering = ''
                        
                    try:
                        for state in faction.PendingStates:
                            if len(pending) > 0:
                                pending = pending + '|'
                            pending = pending + state.State
                    except AttributeError as e:
                        pending = ''
                    
                    insert_influence = "INSERT INTO influence(faction, system, influence, tick, states, pending, recovering) VALUES($1, $2, $3, $4, $5, $6, $7) ON CONFLICT DO NOTHING"
                    influence_values = (
                        faction_id,
                        system_id,
                        faction.Influence * 100,
                        self.tick_id,
                        states,
                        pending,
                        recovering
                    )
                    if faction_id in (75253, 23831, 74847):
                        our_faction = self.faction_data[faction_id]
                        our_influence = faction.Influence * 100
                        our_id = faction_id
                        our_faction.set_recovering(recovering)
                        our_faction.set_active(states)
                        our_faction.set_pending(pending)
                    
                    influences.append(faction.Influence * 100)
                    await db.execute(insert_influence, *influence_values)
                update_system = "UPDATE star_system SET our_faction_id = $1 WHERE id = $2"
                await db.execute(update_system, *(our_id, system_id))
                try:
                    for conflict in data.Conflicts:
                        faction1 = await self._get_faction_id(conflict.Faction1.Name)
                        faction2 = await self._get_faction_id(conflict.Faction2.Name)
                        if faction1 in (75253, 23831, 74847) or faction2 in (75253, 23831, 74847):
                            war_type = conflict.WarType.capitalize()
                            score1 = conflict.Faction1.WonDays
                            score2 = conflict.Faction2.WonDays
                            if war_type is "Civilwar":
                                war_type = "Civil war"
                            if data.StarSystem not in self.war_cache or self.war_cache[data.StarSystem] != score1 + score2:
                                self.war_cache[data.StarSystem] = score1 + score2
                                if faction1 in (75253, 23831, 74847):
                                    conflict_data = ("{} in {}".format(war_type, data.StarSystem), "{} - {}".format(score1, score2))
                                else:
                                    conflict_data = ("{} in {}".format(war_type, data.StarSystem), "{} - {}".format(score2, score1))
                except AttributeError as e:
                    conflict_data = None
            else:
                skip = True
        if not skip:
            print(data.StarSystem + " recorded")
            influences.sort(reverse=True)

            if data.StarSystem in self.updated_systems:
                for item in our_faction.expansion_warning:
                    if data.StarSystem in item:
                        our_faction.expansion_warning.remove(item)
                for item in our_faction.mild_warning:
                    if data.StarSystem in item:
                        our_faction.mild_warning.remove(item)
                for item in our_faction.not_control:
                    if data.StarSystem in item:
                        our_faction.not_control.remove(item)
                for item in our_faction.high_warning:
                    if data.StarSystem in item:
                        our_faction.high_warning.remove(item)

            if our_influence > 65.00:
                our_faction.expansion_warning.append("{} {}%".format(data.StarSystem, round(our_influence, 2)))
            else:
                if our_influence == influences[0]:
                    difference = our_influence - influences[1]
                else:
                    difference = our_influence - influences[0]
                if 10.00 < difference <= 20.00:
                    our_faction.mild_warning.append(
                        "{} {}% ({})".format(data.StarSystem, round(our_influence, 2), round(difference, 2)))
                elif difference < 0.00:
                    our_faction.not_control.append(
                        "{} {}% ({})".format(data.StarSystem, round(our_influence, 2), round(difference, 2)))
                elif difference <= 10.00:
                    our_faction.high_warning.append(
                        "{} {}% ({})".format(data.StarSystem, round(our_influence, 2), round(difference, 2)))
            await self.update_message(our_id, conflict_data)
                
        await database.Database.close_connection(db)
            
        
def setup(bot):
    bot.add_cog(BGS(bot))

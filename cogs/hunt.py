import asyncio

import discord
from discord.ext import commands

import checks
import config
import database
from web import Web
from data.links import award_link

import json
from os import path
import random
from datetime import datetime, timedelta


class Hunt(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.post_init = False
        self.allowed = False
        self.base_chance = 500
        self.base_reward = 100
        self.hunt_cap_ratio = 0.5
        self.lifetime = 1
        self.channels = []
        self.spawn_chance = 0
        self.hunts = {}
        self.reaction = '🐇'
        self.hunt_reactions = []
        self.capture_reactions = []
        self.guaranteed = False

    def initialize_hunt(self):
        if path.isfile(config.BASE_DIR + 'hunt_settings.json'):
            with open(config.BASE_DIR + 'hunt_settings.json') as json_file:
                data = json.load(json_file)
                try:
                    self.base_chance = data['base_chance']
                    self.allowed = data['allowed']
                    self.channels = data['channels']
                    self.hunt_reactions = data["hunt_reactions"]
                    self.capture_reactions = data["capture_reactions"]
                    self.base_reward = data["base_reward"]
                    self.hunt_cap_ratio = data["hunt_cap_ratio"]
                    self.lifetime = data["lifetime"]
                except Exception as e:
                    pass
        self.spawn_chance = self.base_chance
        self.post_init = True

    def save_settings(self):
        settings = {
            "base_chance": self.base_chance,
            "allowed": self.allowed,
            "channels": self.channels,
            "hunt_reactions": self.hunt_reactions,
            "capture_reactions": self.capture_reactions,
            "base_reward": self.base_reward,
            "hunt_cap_ratio": self.hunt_cap_ratio,
            "lifetime": self.lifetime
        }
        with open(config.BASE_DIR + 'hunt_settings.json', 'w') as outfile:
            json.dump(settings, outfile)

    def clean_hunts(self):
        for hunt in tuple(self.hunts):
            if datetime.utcnow() > self.hunts[hunt].end_time:
                self.hunts.pop(hunt)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if not self.post_init:
            return
        if self.allowed is not True:
            return

        # check if the message have a rabbit on it
        self.clean_hunts()
        if reaction.message.id not in self.hunts:
            return
        hunt_data = self.hunts.get(reaction.message.id)

        # check if the player already reacted for this rabbit
        if user.id in hunt_data.players:
            return

        hunting = str(reaction) in self.hunt_reactions
        capturing = str(reaction) in self.capture_reactions
        # check if the reaction is correct
        if hunting or capturing:
            hunt_data.players.append(user.id)

            hunted = 0
            captured = 0
            today = datetime.utcnow()

            reward = 0
            
            mod = 0

            if hunting:
                mod = -100
                hunted = 1
                reward = self.base_reward * self.hunt_cap_ratio
                hunt_data.hunted += 1
            if capturing:
                mod = 50
                captured = 1
                reward = self.base_reward * (1 - self.hunt_cap_ratio)
                hunt_data.captured += 1

            if hunt_data.hunted + hunt_data.captured > 1:
                reward = reward/10
            else:
                self.spawn_chance += mod

            values = {
                'giver': self.bot.user.id,
                # 'giver': 294171600478142466,
                'receiver': user.id,
                # 'receiver': 294171600478142466,
                'amount': round(reward),
                'key': config.TRANSACTION_KEY,
                'type': "diamonds"
            }
            response = await Web.get_response(award_link, values)

            if self.spawn_chance > self.base_chance * 2:
                self.spawn_chance = self.base_chance * 2
            elif self.spawn_chance < self.base_chance / 4:
                self.spawn_chance = self.base_chance / 4

            insert_hunt = "INSERT INTO hunt (user_id, month, year, hunted, captured) VALUES ($1, $2, $3, $4, $5) ON CONFLICT (user_id, month, year) DO UPDATE SET hunted = hunt.hunted + $4, captured = hunt.captured + $5"
            hunt_insert_data = (
                str(user.id),
                today.month,
                today.year,
                hunted,
                captured
            )

            insert_user = "INSERT INTO users (user_id, message_count, reaction_count, special, ducks) VALUES ($1, 0, 0, 0, 1) ON CONFLICT (user_id) DO UPDATE SET ducks = users.ducks + 1"
            db = await database.Database.get_connection(self.bot.loop)

            async with db.transaction():
                await db.execute(insert_user, str(user.id))
                await db.execute(insert_hunt, *hunt_insert_data)
            await database.Database.close_connection(db)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):

        if not self.post_init:
            return
        if self.allowed is not True:
            return
        if message.channel.id not in self.channels:
            return
        number = random.randint(1, 10000)

        if number <= self.spawn_chance or self.guaranteed:
            await asyncio.sleep(random.randint(1, 30))
            self.guaranteed = False
            hunt_data = HuntData(self.bot.user.id, self.lifetime)
            self.hunts[message.id] = hunt_data
            try:
                await message.add_reaction(self.reaction)
            except discord.errors.NotFound as ex:
                self.spawn_chance = 10000
                print("spawning on a removed message, guaranteeing next spawn")

    @commands.group(name='hunt', case_insensitive=True)
    @commands.check(checks.can_manage_bot)
    async def _hunt(self, ctx):
        """
        *Admin only* | Set of commands to control the hunt minigame. `?help hunt` for more info.

        Here is a list of all possible subcommands:
        """
        # group of commands for hunt manipulation
        # if used by itself, it'll show an embed with current state of the hunt
        await ctx.message.delete()
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(colour=discord.Colour(0xF8F8FF), title='Hunt settings', description="Here you can see an overview of the hunt settings and the current state")

            state = "Stoped"
            if self.allowed:
                state = "Active"
            embed.add_field(name="State", value=state)
            embed.add_field(name="Base spawn chance", value="{}%".format(self.base_chance / 100))
            chance = self.spawn_chance
            embed.add_field(name="Spawn chance", value="{}%".format(chance / 100))

            embed.add_field(name="Base reward", value="{} <:diamond:230281835119247361>".format(self.base_reward))
            embed.add_field(name="Hunt modifier", value="{}%".format(self.hunt_cap_ratio * 100))
            embed.add_field(name="Capture modifier", value="{}%".format((1 - self.hunt_cap_ratio) * 100))

            embed.add_field(name="Hunt timeout", value="{} minutes".format(self.lifetime))
            channels = []
            for channel_id in self.channels:
                channel = self.bot.get_channel(channel_id)
                channels.append(channel.name)
            embed.add_field(name="Channels", value=", ".join(channels))
            embed.add_field(name="Hunt emoji", value=" ".join(self.hunt_reactions))
            embed.add_field(name="Capture emoji", value=" ".join(self.capture_reactions))

            embed.set_footer(text="Please refer to `?help hunt` in order to change the settings")
            await ctx.send(embed=embed)

    @_hunt.command(name='start', case_insensitive=True)
    @commands.check(checks.can_manage_bot)
    async def _start(self, ctx):
        """
        *Admin only* | Starts the hunting minigame
        """
        self.allowed = True
        self.save_settings()

    @_hunt.command(name='stop', case_insensitive=True)
    @commands.check(checks.can_manage_bot)
    async def _stop(self, ctx):
        """
        *Admin only* | Stops the hunting minigame
        """
        self.allowed = False
        self.save_settings()

    @_hunt.command(name='spawn', case_insensitive=True)
    @commands.check(checks.can_manage_bot)
    async def _spawn(self, ctx):
        """
        *Admin only* | Marks next eligible message for guaranteed spawn
        """
        self.guaranteed = True

    @_hunt.command(name='allow', case_insensitive=True)
    @commands.check(checks.can_manage_bot)
    async def _allow(self, ctx):
        """
        *Admin only* | Allows the hunt minigame work in the channel where this command was used
        """
        self.channels.append(ctx.channel.id)
        self.save_settings()

    @_hunt.command(name='deny', case_insensitive=True)
    @commands.check(checks.can_manage_bot)
    async def _deny(self, ctx):
        """
        *Admin only* | Denies the hunt minigame to work in the channel where this command was used
        """
        self.channels.remove(ctx.channel.id)
        self.save_settings()

    @_hunt.command(name="add_hunt", case_insensitive=True)
    @commands.check(checks.can_manage_bot)
    async def _add_hunt_reaction(self, ctx, emoji):
        """
        *Admin only* | Adds the emoji into a list of possible reactions to hunt
        """
        self.hunt_reactions.append(emoji)
        self.save_settings()

    @_hunt.command(name="remove_hunt", aliases=['rm_hunt'], case_insensitive=True)
    @commands.check(checks.can_manage_bot)
    async def _remove_hunt_reaction(self, ctx, emoji):
        """
        *Admin only* | Removes the emoji from a list of possible reactions to hunt
        """
        self.hunt_reactions.pop(emoji)
        self.save_settings()

    @_hunt.command(name="add_capture", aliases=['add_cap'], case_insensitive=True)
    @commands.check(checks.can_manage_bot)
    async def _add_capture_reaction(self, ctx, emoji):
        """
        *Admin only* | Adds the emoji into a list of possible reactions to capture
        """
        self.capture_reactions.append(emoji)
        self.save_settings()

    @_hunt.command(name="remove_capture", aliases=['rm_cap'], case_insensitive=True)
    @commands.check(checks.can_manage_bot)
    async def _remove_capture_reaction(self, ctx, emoji):
        """
        *Admin only* | Removes the emoji from a list of possible reactions to capture
        """
        self.capture_reactions.pop(emoji)
        self.save_settings()

    @_hunt.command(name="set_reward", case_insensitive=True)
    @commands.check(checks.can_manage_bot)
    async def _set_diamond_reward(self, ctx, amount):
        """
        *Admin only* | Sets the base diamond reward for each hunt. This is further affected by the hunt/cap ratio and every participant after the first one gets only 1/10 of reward.
        """
        self.base_reward = amount
        self.save_settings()

    @_hunt.command(name="set_timeout", case_insensitive=True)
    @commands.check(checks.can_manage_bot)
    async def _set_lifetime(self, ctx, time):
        """
        *Admin only* | Sets how long is a hunt actively waiting for reactions. Time is in minutes.
        """
        self.lifetime = int(time)
        self.save_settings()


def setup(bot: commands.Bot):
    bot.add_cog(Hunt(bot))


class HuntData:
    def __init__(self, bot_id: int, timeout: int):
        self.hunted = 0
        self.captured = 0
        self.players = [bot_id]
        self.end_time = datetime.utcnow() + timedelta(minutes=timeout)

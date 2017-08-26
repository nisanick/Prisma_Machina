import discord
from discord.ext import commands
import random

default_chance = 600


class Fun:
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.limit = default_chance

    @commands.command(hidden=True)
    async def awesomenessof(self, ctx, who):
        options = [
            'is Exceeding expectations',
            'Went down by 1 point since last time',
            'Needs to be 20% higher',
            'is 43',
            'is Over safety limits',
            'is Leeking from systems',
            'is Hidden under the sofa',
            'is Defined in 345.654.655 dictionaries as Stunning',
            'is Traveling at warp 6.9',
            'Can get to Beagle Point in less than 5 parsecs',

        ]
        member = await commands.MemberConverter().convert(ctx, who)
        if member.id == 205504598792863744:
            await ctx.send("Awesomeness of Wisewolf {}".format(random.choice(options)))
        elif member.id == 186829544764866560:
            await ctx.send("BY ACHENAR... you compared to almighty Wisewolf? Please")
        elif member.id == 152527690291871745:
            await ctx.send("[REDACTED BY ADMINISTRATION - Clasified information]")
        elif member.id == 184799127807328258:
            await ctx.send("Her awesomeness will be greatly missed in our hearts. May her soul find its place amongst the eagles of the Empire.")
        else:
            await ctx.send("You will never be as awesome as Wisewolf")

    @commands.command(hidden=True)
    async def fix(self, ctx: commands.Context, message_id):
        channel = ctx.guild.get_channel(338128432947003392)
        msg = await channel.get_message(int(message_id))

        embed = discord.Embed(color=discord.Colour.gold(),title="::THE PEOPLE’S MEDIA:: - The Daily Chat", description="Breaking news filled the HoloStreams today as hundreds of witnesses reported seeing a phantom floating around the streets of Capitol City.  The ghostly figure resembled **Senator Adonis Manu** and he was heard reciting a mashup of his lectures.  While we would like to claim that the ghost is the haunting return of the late Senator there is official investigations proving that the ghost is a hologram broadcasting segments of recorded lectures.  We will spend an hour discussing the taboo of such a hoax and attempt to find a motivation.  Additionally, **The Administration of the Overseer** are taking control of the investigation giving us a clue that this hoax may be more sinister than an elaborate prank.")
        embed.set_author(name="Alicia Mellor")
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/302178821405278208/342186320384491523/TheDailyChat.png?width=508&height=678")
        embed.set_footer(text="Only on The People’s Media, Your Voice in the Empire and the Stars Beyond.")
        await msg.edit(embed=embed)

    async def on_message(self, message: discord.Message):
        number = random.randint(1, 1000)
        if message.author.id == 186829544764866560 and message.content.lower().__contains__("by achenar"):
            await message.add_reaction(random.choice(['🍺', '🍷', '🍸', '🍹', '🥃']))

        if message.content.lower().__contains__("hi bot"):
            emoji = self.bot.get_emoji(340954397502865409)
            if emoji:
                await message.add_reaction(emoji)

        if number > self.limit:
            if message.content.lower().__contains__("tharg"):
                emoji = discord.utils.get(message.guild.emojis, name='tinfoilhat')
                await message.add_reaction(emoji or '👽')
                self.limit = default_chance

            if message.content.__contains__("Vigor"):
                emoji = discord.utils.get(message.guild.emojis, name='vigor')
                await message.add_reaction(emoji)
                self.limit = default_chance

            if message.content.__contains__("Sight"):
                emoji = discord.utils.get(message.guild.emojis, name='sight')
                await message.add_reaction(emoji)
                self.limit = default_chance

            if message.content.__contains__("Mind"):
                emoji = discord.utils.get(message.guild.emojis, name='mind')
                await message.add_reaction(emoji)
                self.limit = default_chance

            if message.content.__contains__("Aurora"):
                emoji = discord.utils.get(message.guild.emojis, name='aurora')
                await message.add_reaction(emoji)
                self.limit = default_chance

            if message.content.lower().__contains__("aisling") or message.content.lower().__contains__("duval"):
                emoji = discord.utils.get(message.guild.emojis, name='aislingduval')
                await message.add_reaction(emoji)
                self.limit = default_chance

            if message.content.lower().__contains__("kumo") or message.content.lower().__contains__("burger"):
                emoji = discord.utils.get(message.guild.emojis, name='KumoBurger')
                await message.add_reaction(emoji)
                self.limit = default_chance
        else:
            self.limit = self.limit - 10


def setup(bot: commands.Bot):
    bot.add_cog(Fun(bot))

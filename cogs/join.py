import json
import discord
from discord.ext import commands

def load_welcome_channels():
    try:
        with open('welcome_channels.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_welcome_channels(welcome_channels):
    with open('welcome_channels.json', 'w') as file:
        json.dump(welcome_channels, file, indent=4)

welcome_channels = load_welcome_channels()

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def setwelcome(self, ctx, channel: discord.TextChannel):
        welcome_channels[ctx.guild.id] = channel.id
        save_welcome_channels(welcome_channels)
        await ctx.send(f'Welcome message will be send in {channel.mention}')

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel_id = welcome_channels.get(member.guild.id)
        if channel_id:
            channel = self.bot.get_channel(channel_id)
            if channel:
                await channel.send(f'Welcome to the server, {member.mention}! We are glad to have you here.')

async def setup(bot):
    await bot.add_cog(Welcome(bot))


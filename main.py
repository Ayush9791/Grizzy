import discord
from discord.ext import commands
import asyncio
import os
from cogs.server import server
from datetime import datetime

intents = discord.Intents.default()
intents.message_content = True

time = datetime.now()

client = discord.Client()
bot = commands.Bot(command_prefix='~', intents=intents)

for filename in os.listdir("./cogs"):
    if filename.endswith('.py'):
        bot.load_extensions(f'cogs.{filename[:-3]}')

@bot.event
async def on_ready():
    logc = bot.get_channel(1284555765398372374)
    await bot.change_presence(status=discord.Status.do_not_disturb, activity=discord.Activity(type=discord.ActivityType.watching, name="Checking"))
    await logc.send(f"Bot active: {time}")
    print(f'Bot in action as {bot.user}')

@bot.event
async def on_disconnect():
    logc = bot.get_channel(1284555765398372374)
    await logc.send("Bot getting updated")    

@bot.event
async def on_member_join(member):
    welcomec = bot.get_channel(1284945847951298702)
    welcome_message = f'Welcome to the server, {member.mention}! We are glad to have you here.'
    await welcomec.send(welcome_message)

bot.run('MTI3MTkwMDMyNDY0MjI5MTg4NA.G3a5rj.GiY2qZSwku5iH4P3HRC50tQikSh9fIWqXyAU-M')

import discord
from discord.ext import commands
import asyncio
import os
from datetime import datetime
import streamlit as st

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True

time = datetime.now()

client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix=['~','~','?'], intents=intents)

@bot.event
async def on_ready():
    time = datetime.now()
    logc = bot.get_channel(1284555765398372374)
    await bot.change_presence(status=discord.Status.do_not_disturb, activity=discord.Activity(type=discord.ActivityType.listening, name="Matrix"))
    await logc.send(f"Bot active: {time}")
    print(f'Bot in action as {bot.user}')

@bot.event
async def on_disconnect():
    logc = bot.get_channel(1284555765398372374)
    await logc.send("Bot getting updated")    

@bot.event
async def on_member_join(member):
    welcomec = bot.get_channel(1284945847951298702)
    welcome_message = (f'Welcome to the server, {member.mention}! We are glad to have you here.')
    await welcomec.send(welcome_message)


async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith('.py'):
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
            except Exception as e:
                print(f'Failed to load extension {filename[:-3]}: {e}')

token = os.getenv('bot_token')

async def main():
    await load_cogs()
    await bot.start('MTI3MTkwMDMyNDY0MjI5MTg4NA.GLenV-.q1ARaf46gbjECRsqjxXLERgau_d7lDy795gLJ0')

asyncio.run(main())

import discord
from discord.ext import commands

class server(commands.Cog):

    def __init__(self,bot):
        self.bot = bot

    @commands.command()
    async def ping(self,ctx):
        await ctx.send(f"beep beep boop boop!! ping is **{round(self.bot.latency*1000)}ms**")

    @commands.command()
    async def ownerinfo(self, ctx):
        await ctx.send(f'This bot was created by ._Ayush_., join server for more info')

    @commands.command()
    async def mainserver(self, ctx):
        await ctx.send(f'Looks like you need our main server link , Here it is: https://discord.gg/a76qk6Pba5 ')

async def setup(bot):
    await bot.add_cog(server(bot))

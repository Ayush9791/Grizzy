import discord
from discord.ext import commands

class BasicCmds(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def speak(self, ctx, *, arg):
        await ctx.send(arg)

    @commands.command()
    async def gn(self, ctx, *, arg):
        await ctx.send(f'Good night!! {arg}')

    @commands.command()
    async def gm(self, ctx, *, arg):
        await ctx.send(f'Good morning!! {arg}')

async def setup(bot):
    await bot.add_cog(BasicCmds(bot))

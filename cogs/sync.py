import discord
from discord.ext import commands

class CommandManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def sync(self, ctx):
        await self.bot.tree.sync()
        await ctx.send("Commands synced globally.")

async def setup(bot):
    await bot.add_cog(CommandManager(bot))

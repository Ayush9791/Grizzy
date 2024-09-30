import discord
from discord.ext import commands

class CommandManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()  # Only the owner can use this command
    async def sync(self, ctx):
        """Syncs global commands across all servers."""
        await self.bot.tree.sync()  # Sync commands
        await ctx.send("Commands synced globally.")

async def setup(bot):
    await bot.add_cog(CommandManager(bot))

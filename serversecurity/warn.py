import discord
from discord.ext import commands
import json
import os

class Warn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.warnings = {}
        self.load_warnings()

    def load_warnings(self):
        if os.path.exists("warnings.json"):
            with open("warnings.json", "r") as f:
                self.warnings = json.load(f)
        else:
            self.warnings = {}

    def save_warnings(self):
        with open("warnings.json", "w") as f:
            json.dump(self.warnings, f)

    @commands.command(name="warn")
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member: discord.Member, *, reason: str):
        if member.id not in self.warnings:
            self.warnings[member.id] = []
        self.warnings[member.id].append(reason)
        self.save_warnings()
        await ctx.send(f"{member.mention} has been warned for: {reason}")

    @commands.command(name="warnings")
    @commands.has_permissions(manage_messages=True)
    async def warnings(self, ctx, member: discord.Member):
        if member.id in self.warnings and self.warnings[member.id]:
            warnings_list = self.warnings[member.id]
            warnings = '\n'.join(f"{idx+1}. {warn}" for idx, warn in enumerate(warnings_list))
            await ctx.send(f"{member.mention} has the following warnings:\n{warnings}")
        else:
            await ctx.send(f"{member.mention} has no warnings.")

    @commands.command(name="clearwarnings")
    @commands.has_permissions(manage_messages=True)
    async def clear_warnings(self, ctx, member: discord.Member):
        if member.id in self.warnings:
            self.warnings[member.id] = []
            self.save_warnings()
            await ctx.send(f"All warnings for {member.mention} have been cleared.")
        else:
            await ctx.send(f"{member.mention} has no warnings to clear.")

async def setup(bot):
    await bot.add_cog(Warn(bot))

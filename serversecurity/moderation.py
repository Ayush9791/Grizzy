import discord
from discord.ext import commands
from datetime import timedelta

class ModerationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban_member(self, ctx, member: discord.Member, *, reason=None):
        try:
            await member.ban(reason=reason)
            await ctx.send(f"✅ {member.mention} has been banned. Reason: {reason if reason else 'No reason provided.'}")
        except discord.Forbidden:
            await ctx.send("I do not have permission to ban this member.")
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

    @commands.command(name="timeout")
    @commands.has_permissions(moderate_members=True)
    async def timeout_member(self, ctx, member: discord.Member, duration: int, *, reason=None):
        try:
            timeout_duration = timedelta(minutes=duration)
            await member.edit(timed_out_until=discord.utils.utcnow() + timeout_duration, reason=reason)
            await ctx.send(f"✅ {member.mention} has been timed out for {duration} minutes. Reason: {reason if reason else 'No reason provided.'}")
        except discord.Forbidden:
            await ctx.send("I do not have permission to timeout this member.")
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")


    @ban_member.error
    @timeout_member.error
    async def command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You do not have the required permissions to use this command.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Missing required arguments. Please check the command usage.")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("Invalid argument provided. Please check the command usage.")
        else:
            await ctx.send(f"An unexpected error occurred: {error}")

async def setup(bot):
    await bot.add_cog(ModerationCog(bot))

import discord
from discord.ext import commands
import yt_dlp
from discord import FFmpegPCMAudio

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def join(self, ctx):
        """Make the bot join the voice channel"""
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            await channel.connect()
        else:
            await ctx.send("You're not in a voice channel!")

    @commands.command()
    async def leave(self, ctx):
        """Make the bot leave the voice channel"""
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
        else:
            await ctx.send("I'm not in a voice channel!")

    @commands.command()
    async def play(self, ctx, url):
        """Play music from a YouTube URL using yt-dlp and FFmpeg"""
        voice_client = ctx.voice_client
        if not voice_client:
            if ctx.author.voice:
                channel = ctx.author.voice.channel
                voice_client = await channel.connect()
            else:
                await ctx.send("You're not in a voice channel!")
                return

        # yt-dlp options
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'no_warnings': True,
        }

        # Extract audio URL using yt-dlp
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_url = info['formats'][0]['url']

        # FFmpeg options
        ffmpeg_opts = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn'
        }

        # Play audio using FFmpeg
        voice_client.play(FFmpegPCMAudio(audio_url, **ffmpeg_opts), after=lambda e: print(f'Error: {e}') if e else None)
        await ctx.send(f'Now playing: {info["title"]}')

    @commands.command()
    async def pause(self, ctx):
        """Pause the currently playing song"""
        voice_client = ctx.voice_client
        if voice_client.is_playing():
            voice_client.pause()
            await ctx.send("Music paused.")
        else:
            await ctx.send("No music is playing.")

    @commands.command()
    async def resume(self, ctx):
        """Resume the currently paused song"""
        voice_client = ctx.voice_client
        if voice_client.is_paused():
            voice_client.resume()
            await ctx.send("Music resumed.")
        else:
            await ctx.send("No music is paused.")

    @commands.command()
    async def stop(self, ctx):
        """Stop the currently playing song"""
        voice_client = ctx.voice_client
        if voice_client.is_playing():
            voice_client.stop()
            await ctx.send("Music stopped.")
        else:
            await ctx.send("No music is playing.")


def setup(bot):
    bot.add_cog(Music(bot))

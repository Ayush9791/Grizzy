import discord
from discord.ext import commands
import yt_dlp
from discord import FFmpegPCMAudio
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import re
import os

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = []  # Initialize a queue for the songs
        self.volume = 1.0  # Default volume (1.0 = 100%)

        # Spotify API setup
        SPOTIFY_CLIENT_ID = 'your_spotify_client_id'
        SPOTIFY_CLIENT_SECRET = 'your_spotify_client_secret'
        
        self.sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET
        ))

    @commands.command()
    async def join(self, ctx):
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            voice_client = await channel.connect()
            await voice_client.deafen(True)
        else:
            await ctx.send("Lnd ke join toh kr phele voice channel")

    @commands.command()
    async def leave(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("Otte saar 🫡")
            self.queue.clear()  # Clear the queue when leaving
        else:
            await ctx.send("Me toh hue 9😛")

    def get_spotify_track_info(self, url):
        match = re.match(r'https://open.spotify.com/track/([a-zA-Z0-9]+)', url)
        if not match:
            return None

        track_id = match.group(1)
        result = self.sp.track(track_id)
        track_name = result['name']
        artist_name = result['artists'][0]['name']

        return f"{track_name} by {artist_name}"

    def search_youtube(self, query):
        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'extractaudio': True,
            'keepvideo': False,
            'quiet': True,
            'cookiefile': 'youtube_cookies.txt',
            'geo-bypass': True,
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36'
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
                return info['url'], info['title']
            except Exception as e:
                print(f"Bemchoo error aarha {e}")
                return None, None

    async def play_song(self, ctx, url):
        voice_client = ctx.voice_client
        if not voice_client:
            if ctx.author.voice:
                channel = ctx.author.voice.channel
                voice_client = await channel.connect()
            else:
                await ctx.send("Lnd ke join toh kr phele voice channel")
                return

        ffmpeg_opts = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': f'-vn -filter:a "volume={self.volume}"'  # Adjust volume
        }

        voice_client.play(FFmpegPCMAudio(url, **ffmpeg_opts), after=lambda e: self.after_play(ctx, e))

    def after_play(self, ctx, error):
        if error:
            print(f"Error: {error}")
        if self.queue:  # Check if there are more songs in the queue
            next_song = self.queue.pop(0)
            self.bot.loop.create_task(self.play_song(ctx, next_song[0]))  # Play the next song in queue

    @commands.command()
    async def play(self, ctx, *, query):
        voice_client = ctx.voice_client
        if not voice_client:
            if ctx.author.voice:
                channel = ctx.author.voice.channel
                voice_client = await channel.connect()
            else:
                await ctx.send("Lnd ke join toh kr phele voice channel")
                return

        try:
            if query.startswith("https://open.spotify.com/track/"):
                track_info = self.get_spotify_track_info(query)
                if track_info:
                    await ctx.send(f"Now Playing: {track_info}")
                    youtube_url, title = self.search_youtube(track_info)

                    if youtube_url:
                        if not voice_client.is_playing() and len(self.queue) == 0:  # Ensure it's only playing if queue is empty
                            await self.play_song(ctx, youtube_url)  # Play the song immediately
                        else:
                            self.queue.append((youtube_url, title))  # Add to queue
                            await ctx.send(f"Added to queue: {title}")
                    else:
                        await ctx.send("Could not find the song on YouTube.")
                else:
                    await ctx.send("Invalid Spotify link!")
            else:
                # Handle YouTube search or URL
                await self.play_youtube(ctx, query)

        except Exception as e:
            await ctx.send(f"Error aagya bemchooo {e}")
            print(f"Error in play command: {e}")

    async def play_youtube(self, ctx, query):
        """Play from a YouTube search query or URL"""
        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'extractaudio': True,
            'keepvideo': False,
            'quiet': True,
            'cookiefile': 'youtube_cookies.txt',
            'geo-bypass': True,
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36'
        }

        try:
            # Check if the input is a URL or a search query
            if not query.startswith("http"):
                search_query = f"ytsearch:{query}"
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(search_query, download=False)['entries'][0]
            else:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(query, download=False)

            audio_url = info['url']
            title = info['title']
            await ctx.send(f"Now playing: {title}")

            if not ctx.voice_client.is_playing():  # Play if not already playing
                await self.play_song(ctx, audio_url)  # Play the song immediately
            else:
                self.queue.append((audio_url, title))  # Add to queue if already playing
                await ctx.send(f"Dal dia queue me 😏: {title}")

        except Exception as e:
            await ctx.send(f"Error aagya bemchooo : {e}")
            print(f"Error in play_youtube command: {e}")

    @commands.command()
    async def setvolume(self, ctx, volume: int):
        """Set the volume of the player"""
        if 0 <= volume <= 100:
            self.volume = volume / 100  # Scale volume to 0.0 - 1.0
            await ctx.send(f"Volume set to {volume}%")
            # Adjust currently playing song's volume if applicable
            if ctx.voice_client.is_playing():
                ctx.voice_client.stop()  # Stop current playing to apply new volume
                current_url = ctx.voice_client.source.url
                await self.play_song(ctx, current_url)  # Play with new volume
        else:
            await ctx.send("Volume should be between 0 and 100.")

    @commands.command()
    async def download(self, ctx, *, url):
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': '%(title)s.%(ext)s',
            'cookiefile': 'youtube_cookies.txt',
            'geo-bypass': True,
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36'
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info['title']

                filename = f"{title}.mp3"

                # Check Discord's file size limit before sending
                if os.path.getsize(filename) < 8 * 1024 * 1024:  # 8MB limit for free accounts
                    await ctx.send(f"Downloaded: {filename}")
                    await ctx.send(file=discord.File(filename))
                else:
                    await ctx.send("The file is too large to be sent via Discord.")
                
                os.remove(filename)
            
        except yt_dlp.DownloadError as e:
            await ctx.send(f"Download failed: {e}")
        except Exception as e:
            await ctx.send(f"Error occurred: {e}")
            print(f"Error in download command: {e}")


    @commands.command()
    async def pause(self, ctx):
        voice_client = ctx.voice_client
        if voice_client.is_playing():
            voice_client.pause()
            await ctx.send("le re krdia pause")
        else:
            await ctx.send("Abbey gndu phele gana chla toh")

    @commands.command()
    async def resume(self, ctx):
        voice_client = ctx.voice_client
        if voice_client.is_paused():
            voice_client.resume()
            await ctx.send("Ruk ruk krta chlu wapas")
        else:
            await ctx.send("lodu koi gana pause he nhi h")

    @commands.command()
    async def stop(self, ctx):
        voice_client = ctx.voice_client
        if voice_client.is_playing():
            voice_client.stop()
            await ctx.send("Krdia bnd")
        else:
            await ctx.send("Gana chl he nhi rha 😛😛")

    @commands.command()
    async def queue(self, ctx):
        if not self.queue:
            await ctx.send("Phele queue me dal to de kuch")
        else:
            queue_list = "\n".join(f"{i + 1}. {title}" for i, (url, title) in enumerate(self.queue))
            await ctx.send(f"Current queue:\n{queue_list}")

    @commands.command()
    async def skip(self, ctx):
        voice_client = ctx.voice_client
        if voice_client.is_playing():
            voice_client.stop()
            await ctx.send("Le re krdia skip")
        else:
            await ctx.send("Kya bhai koi gana nahi chal raha hai!")

async def setup(bot):
    await bot.add_cog(Music(bot))


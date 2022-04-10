from __future__ import unicode_literals
import discord
import asyncio
from discord.ext import commands
from discord_webhook import DiscordWebhook
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from youtubesearchpython import VideosSearch
import youtube_dl
import os


bot = commands.Bot(command_prefix='!')
TOKEN = "OTQ5OTYxODU1NDQ5ODQ5ODc2.YiR-6w.azhDOCmYS-sngzTHtHI7sqrZPnM"
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

'''SpotifyApi'''
client_id = "78a7bbd4b14d44f089471f96cff65c7f"  # Сюда вводим полученные данные из панели спотифая
secret = "a9052a01b1a94306851d93742998921d"  # Сюда вводим полученные данные из панели спотифая

auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=secret)
spotify = spotipy.Spotify(auth_manager=auth_manager)

url = ''
sp_music = []

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    for guild in bot.guilds:
        print(
            f'{bot.user} подключились к чату:\n'
            f'{guild.name}(id: {guild.id})')


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    else:
        pass
    await bot.process_commands(message)


@bot.command('плейлист')
async def playlist(ctx):
    url = ctx.message.content[9:-1]
    result = spotify.track(url)
    author = result['artists'][0]['name']
    name_music = result['name']
    sp_music.append(f"{author} - {name_music}")
    print(sp_music)



@bot.command('старт')
async def start_music(ctx):
    voice_channel = ctx.message.author.voice.channel
    vc = await voice_channel.connect()
    play_music(ctx, vc)


@bot.command('стоп')
async def stop_music(ctx):
    global sp_music
    sp_music = []
    await ctx.voice_client.disconnect()


def play_music(ctx, vc):
    url_music = music_url(sp_music[0])
    del sp_music[0]
    vc.play(discord.FFmpegPCMAudio(executable="ffmpeg.exe", source=url_music, **FFMPEG_OPTIONS),
            after=lambda e: play_music(ctx, vc))


def music_url(music_info):
    videosSearch = VideosSearch(music_info, limit=1)

    ydl = youtube_dl.YoutubeDL({'format': 'bestaudio/best',
                                'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3',
                                                    'preferredquality': '192'}],
                                'outtmpl': f'./music.webm'})
    url_music = videosSearch.result()["result"][0]["link"]
    with ydl:
        result = ydl.extract_info(url_music, download=False)
    return result['formats'][0]['url']


bot.run(TOKEN)

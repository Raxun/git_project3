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
TOKEN = ""
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

'''SpotifyApi'''
client_id = ""  # Сюда вводим полученные данные из панели спотифая
secret = ""  # Сюда вводим полученные данные из панели спотифая

auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=secret)
spotify = spotipy.Spotify(auth_manager=auth_manager)

sp_music = []

em_help = discord.Embed(title="", colour=0x87CEEB)
em_help_music = discord.Embed(title="", colour=0x87CEEB)
em_help.set_author(name="Raxun", icon_url="https://avatars.githubusercontent.com/u/94015674?s=400&u=7d739"
                                              "fe0e1593df54e804fb6e097f597a3a838d7&v=4")
em_help.add_field(name="Команды", value="!музыка", inline=False)
em_help_music.set_author(name="Raxun", icon_url="https://avatars.githubusercontent.com/u/94015674?s=400&u=7d739"
                                                "fe0e1593df54e804fb6e097f597a3a838d7&v=4")
em_help_music.add_field(name="Команды", value="!плейлист (ссылка на трек Spotify) !очистить плейлист !плейлист "
                                              "!стоп !старт !скип", inline=False)


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


@bot.command('помощь')
async def help_command(ctx):
    await ctx.message.channel.send(embed=em_help)


@bot.command('музыка')
async def help_command(ctx):
    await ctx.message.channel.send(embed=em_help_music)


@bot.command('плейлист')
async def playlist(ctx):
    if len(ctx.message.content) > 11:
        url_track = ctx.message.content[9:-1]
        result = spotify.track(url_track)
        print(result)
        author = result['artists'][0]['name']
        name_music = result['name']
        sp_music.append(f"{author} - {name_music}")
        em_playlist = discord.Embed(title="Плейлист", colour=0x87CEEB)
        em_playlist.set_author(name="Raxun", icon_url="https://avatars.githubusercontent.com/u/94015674?s=400&u=7d739"
                                                      "fe0e1593df54e804fb6e097f597a3a838d7&v=4")
        for i, elem in enumerate(sp_music):
            em_playlist.add_field(name=str(i + 1), value=elem, inline=False)
        await ctx.message.channel.send(embed=em_playlist)
        print(sp_music)
    elif len(sp_music) == 0:
        em_playlist = discord.Embed(title="Плейлист пуст!", colour=0x87CEEB)
        em_playlist.set_author(name="Raxun", icon_url="https://avatars.githubusercontent.com/u/94015674?s=400&u=7d739"
                                                      "fe0e1593df54e804fb6e097f597a3a838d7&v=4")
        await ctx.message.channel.send(embed=em_playlist)
    else:
        em_playlist = discord.Embed(title="Плейлист", colour=0x87CEEB)
        em_playlist.set_author(name="Raxun", icon_url="https://avatars.githubusercontent.com/u/94015674?s=400&u=7d739"
                                                      "fe0e1593df54e804fb6e097f597a3a838d7&v=4")
        for i, elem in enumerate(sp_music):
            em_playlist.add_field(name=str(i + 1), value=elem, inline=False)
        await ctx.message.channel.send(embed=em_playlist)


@bot.command('старт')
async def start_music(ctx):
    voice_channel = ctx.message.author.voice.channel
    await voice_channel.connect()
    play_music(ctx)


@bot.command('стоп')
async def stop_music(ctx):
    sp_music.clear()
    await ctx.voice_client.disconnect()


@bot.command('скип')
async def stop_music(ctx):
    ctx.voice_client.stop()
    play_music(ctx)


@bot.command('очистить')
async def stop_music(ctx):
    sp_music.clear()
    em_playlist = discord.Embed(title="Плейлист пуст!", colour=0x87CEEB)
    em_playlist.set_author(name="Raxun", icon_url="https://avatars.githubusercontent.com/u/94015674?s=400&u=7d739"
                                                  "fe0e1593df54e804fb6e097f597a3a838d7&v=4")
    await ctx.message.channel.send(embed=em_playlist)


def play_music(ctx):
    url_music = music_url(sp_music[0])
    del sp_music[0]
    ctx.voice_client.play(discord.FFmpegPCMAudio(executable="ffmpeg.exe", source=url_music, **FFMPEG_OPTIONS),
                          after=lambda e: play_music(ctx))


def music_url(music_info):
    vidsearch = VideosSearch(music_info, limit=1)
    ydl = youtube_dl.YoutubeDL({'format': 'bestaudio/best',
                                'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3',
                                                    'preferredquality': '192'}],
                                'outtmpl': f'./music.webm'})
    url_music = vidsearch.result()["result"][0]["link"]
    with ydl:
        result = ydl.extract_info(url_music, download=False)
    return result['formats'][0]['url']


bot.run(TOKEN)

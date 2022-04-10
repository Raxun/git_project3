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
TOKEN = "BOT_TOKEN"

'''SpotifyApi'''
client_id = "id"  # Сюда вводим полученные данные из панели спотифая
secret = "secret_key"  # Сюда вводим полученные данные из панели спотифая


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


bot.run(TOKEN)

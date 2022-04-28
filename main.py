from __future__ import unicode_literals
import discord
from discord.ext import commands
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from youtubesearchpython import VideosSearch
import youtube_dl
from data import db_session
from data.User import User
from data.Roles import Roles


intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)
TOKEN = ""
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}


'''SpotifyApi'''
client_id = ""  # Сюда вводим полученные данные из панели спотифая
secret = ""  # Сюда вводим полученные данные из панели спотифая

auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=secret)
spotify = spotipy.Spotify(auth_manager=auth_manager)

sp_music = []
music = []

em_help = discord.Embed(title="", colour=0x87CEEB)
em_help_music = discord.Embed(title="", colour=0x87CEEB)
em_roles = discord.Embed(title="Команды для работы с ролями", colour=0x87CEEB)
em_roles.set_author(name="Raxun", icon_url="https://avatars.githubusercontent.com/u/94015674?s=400&u=7d739"
                                           "fe0e1593df54e804fb6e097f597a3a838d7&v=4")
em_help.set_author(name="Raxun", icon_url="https://avatars.githubusercontent.com/u/94015674?s=400&u=7d739"
                                          "fe0e1593df54e804fb6e097f597a3a838d7&v=4")
em_help.add_field(name="Команды", value="!музыка! !лвл !топ !роли", inline=False)
em_help_music.set_author(name="Raxun", icon_url="https://avatars.githubusercontent.com/u/94015674?s=400&u=7d739"
                                                "fe0e1593df54e804fb6e097f597a3a838d7&v=4")
em_help_music.add_field(name="Команды", value="!плейлист (ссылка Spotify/название) !очистить плейлист !плейлист "
                                              "!стоп !старт !скип !трек (последний трек)", inline=False)

members = []


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
        await check_user(message.guild.id, message.author.id, message)
    await bot.process_commands(message)


@bot.event
async def on_guild_join(guild):
    db_session.global_init("db/users_lvl.db")
    db_sess = db_session.create_session()
    roles = db_sess.query(Roles).filter(Roles.id_owner == int(guild.owner.id), Roles.id_server == int(guild.id)).first()
    if roles is None:
        new_server = User()
        new_server.id_owner = guild.owner.id
        new_server.id_server = guild.id
        new_server.banned_role = ''
        new_server.admitted_users = ''
        db_sess.add(new_server)
        db_sess.commit()


@bot.command('помощь')
async def help_command(ctx):
    await ctx.message.channel.send(embed=em_help)


@bot.command('музыка')
async def help_command(ctx):
    await ctx.message.channel.send(embed=em_help_music)


@bot.command('трек')
async def track(ctx):
    em_play = discord.Embed(title="В последний раз играло:", description=music[0], colour=0x87CEEB)
    em_play.set_author(name="Raxun", icon_url="https://avatars.githubusercontent.com/u/94015674?s=400&u=7d739"
                                              "fe0e1593df54e804fb6e097f597a3a838d7&v=4")
    await ctx.message.channel.send(embed=em_play)


@bot.command('плейлист')
async def playlist(ctx):
    if len(ctx.message.content) > 11:
        em_playlist = discord.Embed(title="Плейлист", colour=0x87CEEB)
        em_playlist.set_author(name="Raxun", icon_url="https://avatars.githubusercontent.com/u/94015674?s=400&u=7d739"
                                                      "fe0e1593df54e804fb6e097f597a3a838d7&v=4")
        if 'https://open.spotify.com' in ctx.message.content:
            url_track = ctx.message.content[9:-1]
            result = spotify.track(url_track)
            author = result['artists'][0]['name']
            name_music = result['name']
            sp_music.append(f"{author} - {name_music}")
            em_playlist.description = '\n'.join(sp_music)
            await ctx.message.channel.send(embed=em_playlist)
        else:
            vidsearch = VideosSearch(ctx.message.content[9:-1], limit=1)
            mus_info = vidsearch.result()["result"][0]["title"]
            if mus_info.find('(') != -1:
                name = mus_info[:mus_info.find('(')]
            else:
                name = mus_info
            sp_music.append(name)
            em_playlist.description = '\n'.join(sp_music)
            await ctx.message.channel.send(embed=em_playlist)
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
    if not ctx.voice_client:
        voice_channel = ctx.message.author.voice.channel
        await voice_channel.connect()
    if not ctx.voice_client.is_playing():
        if len(sp_music) != 0:
            em_play = discord.Embed(title="Сейчас играет", description=sp_music[0], colour=0x87CEEB)
            em_play.set_author(name="Raxun", icon_url="https://avatars.githubusercontent.com/u/94015674?s=400&u=7d739"
                                                      "fe0e1593df54e804fb6e097f597a3a838d7&v=4")
            await ctx.message.channel.send(embed=em_play)
            play_music(ctx)
        else:
            em_playlist = discord.Embed(title="Плейлист пуст!", description="Используйте команду !плейлист (название / "
                                                                            "ссылка на spotify) для добавления трека "
                                                                            "в очередь)", colour=0x87CEEB)
            em_playlist.set_author(name="Raxun", icon_url="https://avatars.githubusercontent.com/u/94015674?s=400&u=7d"
                                                          "739fe0e1593df54e804fb6e097f597a3a838d7&v=4")
            await ctx.message.channel.send(embed=em_playlist)
    else:
        em_playerror = discord.Embed(title="Музыка уже играет!", description='Для пропуска используйте команду !скип',
                                     colour=0x87CEEB)
        em_playerror.set_author(name="Raxun", icon_url="https://avatars.githubusercontent.com/u/94015674?s=400&u=7d739"
                                                       "fe0e1593df54e804fb6e097f597a3a838d7&v=4")
        await ctx.message.channel.send(embed=em_playerror)


@bot.command('стоп')
async def stop_music(ctx):
    sp_music.clear()
    await ctx.voice_client.disconnect()


@bot.command('скип')
async def skip_music(ctx):
    ctx.voice_client.stop()
    await start_music(ctx)


@bot.command('очистить')
async def clear_music(ctx):
    sp_music.clear()
    em_playlist = discord.Embed(title="Плейлист пуст!", colour=0x87CEEB)
    await ctx.message.channel.send(embed=em_playlist)


@bot.command('лвл')
async def check_level(ctx):
    db_session.global_init("db/users_lvl.db")
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id_user == int(ctx.message.author.id),
                                      User.id_server == int(ctx.message.guild.id)).first()
    if user is not None:
        user_message = user.NumberOfMessage.split('/')
        em_level_info = discord.Embed(title=f"Ваш уровень - {user.lvl}",
                                      description=f"опыта {user_message[0]} из {user_message[-1]}", colour=0x87CEEB)
        em_level_info.set_author(name="Raxun", icon_url="https://avatars.githubusercontent.com/u/94015674?s=400&"
                                                        "u=7d739fe0e1593df54e804fb6e097f597a3a838d7&v=4")
        await ctx.message.channel.send(embed=em_level_info)
    else:
        new_user = User()
        new_user.id_user = ctx.message.author.id
        new_user.id_server = ctx.message.guild.id
        new_user.NumberOfMessage = '0/10'
        new_user.lvl = 1
        db_sess.add(new_user)
        db_sess.commit()


@bot.command('топ')
async def check_level(ctx):
    db_session.global_init("db/users_lvl.db")
    db_sess = db_session.create_session()
    users = db_sess.query(User).filter(User.id_server == int(ctx.message.guild.id)).order_by(User.lvl.desc()).all()
    sp_top_users = [f"<@{user.id_user}> - {user.lvl} уровень" for user in users]
    em_sp_tops = discord.Embed(title="Топ сервера", colour=0x87CEEB)
    em_sp_tops.set_author(name="Raxun", icon_url="https://avatars.githubusercontent.com/u/94015674?s=400&"
                                                 "=7d739fe0e1593df54e804fb6e097f597a3a838d7&v=4")
    em_sp_tops.description = '\n'.join(sp_top_users)
    await ctx.message.channel.send(embed=em_sp_tops)


@bot.command('роли')
async def roles(ctx):
    db_session.global_init("db/users_lvl.db")
    db_sess = db_session.create_session()
    print(int(ctx.guild.owner.id))
    roles = db_sess.query(Roles).filter(Roles.id_owner == int(ctx.message.guild.owner.id),
                                        Roles.id_server == int(ctx.message.guild.id)).first()
    if roles.id_owner == int(ctx.message.guild.owner.id):
        em_roles.description = '!роль @роль @пользователь !выдача @тег пользователя, который сможет выдать роль ' \
                               '!запрет @тег роли, которую нельзя будет выдать'
    else:
        em_roles.description = '!роль @роль @пользователь'
    await ctx.message.channel.send(embed=em_roles)


@bot.command('выдача')
async def roles(ctx, user):
    db_session.global_init("db/users_lvl.db")
    db_sess = db_session.create_session()
    roles = db_sess.query(Roles).filter(Roles.id_owner == int(ctx.message.guild.owner.id),
                                        Roles.id_server == int(ctx.message.guild.id)).first()
    if roles.id_owner == ctx.message.author.id and '<@' in ctx.message.content:
        roles.admitted_users = f"{roles.admitted_users} {user[3:-1]}"
        complete = discord.Embed(title="Выполнено!", description='Добавлен новый пользователь', colour=0x87CEEB)
        complete.set_author(name="Raxun", icon_url="https://avatars.githubusercontent.com/u/94015674?s=400&"
                                                   "=7d739fe0e1593df54e804fb6e097f597a3a838d7&v=4")
        db_sess.add(roles)
        db_sess.commit()
        await ctx.message.channel.send(embed=complete)
    else:
        if roles.id_owner != ctx.message.author.id:
            error1 = discord.Embed(title="Ошибка!", description='Эту команду может использовать только владелец '
                                                                       'сервера', colour=0x87CEEB)
            error1.set_author(name="Raxun", icon_url="https://avatars.githubusercontent.com/u/94015674?s=400&"
                                                            "=7d739fe0e1593df54e804fb6e097f597a3a838d7&v=4")
            await ctx.message.channel.send(error1)
        else:
            error2 = discord.Embed(title="Ошибка!", description='Введите !выдача @тег пользователя',
                                  colour=0x87CEEB)
            error2.set_author(name="Raxun", icon_url="https://avatars.githubusercontent.com/u/94015674?s=400&"
                                                     "=7d739fe0e1593df54e804fb6e097f597a3a838d7&v=4")
            await ctx.message.channel.send(embed=error2)


@bot.command('запрет')
async def roles(ctx, role):
    db_session.global_init("db/users_lvl.db")
    db_sess = db_session.create_session()
    roles = db_sess.query(Roles).filter(Roles.id_owner == int(ctx.message.guild.owner.id),
                                        Roles.id_server == int(ctx.message.guild.id)).first()
    if roles.id_owner == ctx.message.author.id and '<@' in ctx.message.content:
        roles.banned_role = f"{roles.banned_role} {role[3:-1]}"
        complete = discord.Embed(title="Выполнено!", description='Добавлена новая запрещенная роль', colour=0x87CEEB)
        complete.set_author(name="Raxun", icon_url="https://avatars.githubusercontent.com/u/94015674?s=400&"
                                                 "=7d739fe0e1593df54e804fb6e097f597a3a838d7&v=4")
        db_sess.add(roles)
        db_sess.commit()
        await ctx.message.channel.send(embed=complete)
    else:
        if roles.id_owner != ctx.message.author.id:
            error1 = discord.Embed(title="Ошибка!", description='Эту команду может использовать только владелец '
                                                                       'сервера', colour=0x87CEEB)
            error1.set_author(name="Raxun", icon_url="https://avatars.githubusercontent.com/u/94015674?s=400&"
                                                            "=7d739fe0e1593df54e804fb6e097f597a3a838d7&v=4")
            await ctx.message.channel.send(error1)
        else:
            error2 = discord.Embed(title="Ошибка!", description='Произошла ошибка! введите !запрещенные @тег роли'
                                                                'сервера', colour=0x87CEEB)
            error2.set_author(name="Raxun", icon_url="https://avatars.githubusercontent.com/u/94015674?s=400&"
                                                     "=7d739fe0e1593df54e804fb6e097f597a3a838d7&v=4")
            await ctx.message.channel.send(embed=error2)


@bot.command('роль')
async def roles(ctx, role, user: discord.Member):
    db_session.global_init("db/users_lvl.db")
    db_sess = db_session.create_session()
    roles = db_sess.query(Roles).filter(Roles.id_server == int(ctx.message.guild.id)).first()
    if ' ' in str(roles.admitted_users):
        sp_admitted_users = roles.admitted_users.split(' ')
    else:
        sp_admitted_users = str(roles.admitted_users)
    if ' ' in str(roles.banned_role):
        sp_banned_role = roles.banned_role.split(' ')
    else:
        sp_banned_role = str(roles.banned_role)
    if '<@' in role:
        role_ds = ctx.guild.get_role(int(role[3:-1]))
        if (ctx.message.author.id in sp_admitted_users or ctx.message.author.id == roles.id_owner) \
                and '<@' in ctx.message.content and role[3:-1] not in sp_banned_role:
            await user.add_roles(role_ds)
        else:
            em_info_roles = discord.Embed(title="Ошибка!", description='Эту команду могут использовать только допущенны'
                                                                       'е пользователи, с учетом что роль является разр'
                                                                       'ешенной для выдачи', colour=0x87CEEB)
            em_info_roles.set_author(name="Raxun", icon_url="https://avatars.githubusercontent.com/u/94015674?s=400&"
                                                            "=7d739fe0e1593df54e804fb6e097f597a3a838d7&v=4")
            await ctx.message.channel.send(embed=em_info_roles)
    else:
        em_info_roles = discord.Embed(title="Ошибка!", description='Введите !роль @тег роли @тег пользователя',
                                      colour=0x87CEEB)
        await ctx.message.channel.send(embed=em_info_roles)


async def check_user(server_id, user_id, message):
    db_session.global_init("db/users_lvl.db")
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id_user == int(user_id), User.id_server == int(server_id)).first()
    if message.content[0] != '!':
        if user is not None:
            user_message = user.NumberOfMessage.split('/')
            if user_message[0] == user_message[-1]:
                user.NumberOfMessage = f"{0}/{int(user_message[-1]) * 2}"
                user.lvl = user.lvl + 1
                em_user_level_up = discord.Embed(title="", colour=0x87CEEB)
                em_user_level_up.set_author(name="Raxun", icon_url="https://avatars.githubusercontent.com/u/94015674?s="
                                                                   "400&u=7d739fe0e1593df54e804fb6e097f597a3a838d7&v=4")
                em_user_level_up.add_field(name="Новый уровень", value=f"<@{user.id_user}> теперь {user.lvl} уровня!",
                                           inline=False)
                await message.channel.send(embed=em_user_level_up)
                db_sess.commit()
            else:
                user.NumberOfMessage = f"{int(user_message[0]) + 1}/{user_message[-1]}"
                db_sess.commit()
        else:
            new_user = User()
            new_user.id_user = user_id
            new_user.id_server = server_id
            new_user.NumberOfMessage = '0/10'
            new_user.lvl = 1
            db_sess.add(new_user)
            db_sess.commit()


def play_music(ctx):
    url_music = music_url(sp_music[0])
    del music[:]
    music.append(sp_music[0])
    del sp_music[0]
    ctx.voice_client.play(discord.FFmpegPCMAudio(executable="ffmpeg.exe", source=url_music, **FFMPEG_OPTIONS),
                          after=lambda e: play_music(ctx))


def music_url(music_info):
    try:
        vidsearch = VideosSearch(music_info, limit=1)
        ydl = youtube_dl.YoutubeDL({'format': 'bestaudio/best',
                                    'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3',
                                                        'preferredquality': '192'}],
                                    'outtmpl': f'./music.webm'})
        url_music = vidsearch.result()["result"][0]["link"]
        with ydl:
            result = ydl.extract_info(url_music, download=False)
        return result['formats'][0]['url']
    except RuntimeWarning:
        music_url(music_info)


bot.run(TOKEN)

from pytube import Playlist
from discord.ext import commands
import discord
import asyncio
import os
from pytube import YouTube
import json
from discord import Embed, Interaction
from discord.ui import Button, View
import Levenshtein
import random
import logging

# Setup
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'}
EMBED_COLOR = 0x9b111e

logging.basicConfig(level=logging.INFO,
                    format="[%(asctime)s] %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class Urls:
    # Urls class
    def __init__(self):
        self.radio = \
            json.load(open("cogs/radio.json", "r", encoding="utf-8"))


class Track():
    # Track class
    def __init__(self, author: str, name: str, audio_url: str):
        self.author = author
        self.name = name
        self.url = audio_url

    def __str__(self):
        return "\"" + str(self.author) + ' - ' + str(self.name) + "\": \""\
            + str(self.url[:24]) + "...\""


class AudioExtractor():
    def __init__(self):
        self.ext_msg = None

    async def __youtube(
            self,
            ctx: commands.Context,
            url: str,
            count: int = None):

        # YT playlist
        limit = 0
        if 'playlist' in url:
            logger.info(f"Loading playlist: {url}")
            try:
                playlist = Playlist(url)
                result = []
                if count:
                    limit = min(count, len(playlist.videos))
                else:
                    limit = len(playlist.videos)
                for video in playlist.videos[:limit]:
                    audio = video.streams.filter(only_audio=True).first()
                    name = video.title
                    # Remove blacklisted strings from the name
                    for blacklisted in LEX_BLACKLIST:
                        name = name.replace(blacklisted, '')
                    author = video.author
                    result.append(Track(author, name, audio.url))

                    embed = discord.Embed(title="Загрузка",
                                          description=''
                                          + f"\nЗагружено "
                                          + f"[{len(result)}/{limit}]"
                                          + f" треков",
                                          color=EMBED_COLOR)
                    if self.ext_msg:
                        await self.ext_msg.edit(embed=embed)
                    else:
                        self.ext_msg = await ctx.send(embed=embed)

                    if len(result) == limit:
                        await self.ext_msg.delete()
                        self.ext_msg = None
                    logger.info(f"Loaded track: {str(result[-1])}")
                return result
            except Exception as e:
                logger.error(f"{e}")
                return []

        # YT video
        try:
            logger.info(f"Loading track: {url}")
            yt = YouTube(url)
            audio = yt.streams.filter(only_audio=True).first()
            name = yt.title
            author = yt.author
            return [Track(author, name, audio.url)]
        except Exception as e:
            logger.error(f"{e}")
            return []

    async def extract(
            self,
            ctx: commands.Context,
            url: str,
            msg: discord.Message = None,
            count: int = None):
        if 'youtube' in url:
            return await self.__youtube(ctx, url, count)
        else:
            logger.error(f"Invalid URL: {url}")


# Utility stuff
urls = Urls()
extractor = AudioExtractor()
LEX_BLACKLIST = json.load(
    open("cogs/lexems_blacklist.json", "r", encoding="utf-8"))


class Player(commands.Cog):
    __init__: commands.Bot

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.playlist = []
        self.player_msg = None
        self.player = None

    @commands.command(name="play", description="Воспроизвести трек (YouTube)")
    async def play(
            self,
            ctx: commands.Context,
            url: str = None,
            count: int = None
    ):
        """
        - Воспроизвести трек

        Parameters
        ----------
        ctx : commands.Context
            The context object.
        url : str
            - Ссылка на трек (YouTube)
        count : int
            - Количество треков для воспроизведения
        """

        # Conditions
        def is_author_in_voice():
            return ctx.author.voice.channel

        def is_playing():
            return self.player.is_playing()

        def is_msg_exists():
            return self.player_msg

        def is_playlist_empty():
            return len(self.playlist) == 0

        def is_bot_in_voice():
            return ctx.guild.voice_client

        # Check if the user is in a voice channel
        # if is_author_in_voice():
        if True:

            if not is_msg_exists():
                embed = discord.Embed(
                    title="Плеер",
                    description="",
                    color=EMBED_COLOR)
                self.player_msg = await ctx.send(
                    embed=embed)

            # Delete request message
            await ctx.message.delete()

            # At this point the user is in a voice channel
            # At this point the message exists

            # Extract audio URL
            try:
                self.playlist += await extractor.extract(
                    ctx=ctx,
                    url=url,
                    msg=self.player_msg,
                    count=count)
            except:
                embed = discord.Embed(title="ОШИБКА",
                                      description=f"Неверный URL",
                                      color=EMBED_COLOR)
                await self.player_msg.edit(embed=embed)
                logger.error(f"Invalid URL: {url}")

            # Connect to a voice channel
            if not is_bot_in_voice():
                # Connect to the voice channel
                self.player = await ctx.author.voice.channel.connect()
            else:
                self.player = ctx.guild.voice_client

            # Deafen self
            await ctx.guild.change_voice_state(
                channel=ctx.guild.voice_client.channel,
                self_mute=False,
                self_deaf=True)

            # At this point the user is in a voice channel
            # At this point the bot is in a voice channel
            # At this point the message exists
            # At this point songs added to the playlist

            # If song is playing, return
            if is_playing():
                return

            if not is_playlist_empty():
                # At this point the user is in a voice channel
                # At this point the bot is in a voice channel
                # At this point the message exists
                # At this point the playlist is not empty
                # At this point nothing is playing

                # Play the first song in the playlist
                track = self.playlist.pop(0)

                next_display = 5

                # TODO: queue should update automatically if new tracks added
                next_five = ""
                if min(next_display, len(self.playlist)) > 0:
                    next_five += '\n__Очередь:__'
                    for i in range(min(next_display, len(self.playlist))):
                        next_five += f"\n{i+1}. " + str(self.playlist[i].author) \
                            + " - " + str(self.playlist[i].name)
                    if len(self.playlist) > next_display:
                        next_five += f"\nи еще {len(self.playlist) -
                                                next_display} треков..."

                # Button STOP
                stop_button = discord.ui.Button(
                    style=discord.ButtonStyle.danger, label="Stop")

                async def callback_stop_button(ctx):
                    if is_playing():
                        logger.info(msg="Stopping...")
                        self.player.stop()
                        # update the view
                        stop_button.disabled = True
                        logger.info(msg="Stopped")

                stop_button.callback = callback_stop_button

                skip_button = discord.ui.Button(
                    style=discord.ButtonStyle.blurple, label="Next >>")

                async def callback_skip_button(ctx):
                    if is_playing():
                        self.player.stop()
                skip_button.callback = callback_skip_button

                view = discord.ui.View()
                view.add_item(skip_button)
                view.add_item(stop_button)

                embed = discord.Embed(title="Играет трек",
                                      description="\"__**"
                                      + str(track.author) + ' - ' +
                                      str(track.name) + "**__\"\n" + next_five,
                                      color=EMBED_COLOR)

                await self.player_msg.edit(embed=embed, view=view)

                try:
                    self.player.play(discord.FFmpegPCMAudio(
                        track.url,
                        **FFMPEG_OPTIONS))
                except Exception as e:
                    logger.error(f"{e}")

                # Set the playing status to True
                playing = is_playing()

                # Sleep until the song is done playing
                while playing:
                    await asyncio.sleep(1)
                    playing = is_playing()
            else:
                embed = discord.Embed(title="ОШИБКА",
                                      description=f"Плейлист пуст",
                                      color=EMBED_COLOR)
                await self.player_msg.edit(embed=embed)
                logger.error(f"Playlist is empty")
                logger.error(f"Playlist: {self.playlist}")

            # If there are songs in the playlist, play the next one
            if self.playlist:
                await self.play(ctx)

        else:
            await ctx.send("Пожалуйста, подключитесь к голосовому каналу.")

    @commands.command(name="skip", description="Пропустить трек")
    async def skip(self, ctx: commands.Context, count: int = 1):
        """
        - Пропустить трек

        Parameters
        ----------
        ctx : commands.Context
            The context object.
        count : int
            - Количество треков для пропуска
        """
        try:
            if self.player.is_playing():
                self.player.stop()
        except:
            pass

        # track = self.playlist.pop(0)

        # embed = discord.Embed(title="Играет трек",
        #                       description="\"__**"
        #                       + str(track.author) + ' - ' +
        #                       str(track.name) + "**__\"",
        #                       color=EMBED_COLOR)

        # await self.player_msg.edit(embed=embed)

        # Play the next song in the playlist
        if self.playlist:
            await self.play(ctx)
        await ctx.message.delete()

    @commands.command(name="stop", description="Остановить воспроизведение")
    async def stop(self, ctx: commands.Context):
        """
        - Остановить воспроизведение

        Parameters
        ----------
        ctx : commands.Context
            The context object.
        """
        voice_client = ctx.voice_client
        if voice_client.is_playing():
            voice_client.stop()
        await asyncio.sleep(5)
        await ctx.message.delete()

    @commands.command(name="disconnect", description="Отключиться от голосового канала")
    async def disconnect(self, ctx: commands.Context):
        """
        - Отключиться от голосового канала

        Parameters
        ----------
        ctx : commands.Context
            The context object.
        """
        voice_client = ctx.voice_client
        if voice_client.is_playing():
            voice_client.stop()
        await voice_client.disconnect()
        await asyncio.sleep(5)
        await ctx.message.delete()

    @commands.command(name="radiolist", description="Показать список радиостанций")
    async def radiolist(self, ctx: commands.Context):
        """
        - Показать список радиостанций

        Parameters
        ----------
        ctx : commands.Context
            The context object.
        """

        radio_raw = urls.radio

        # find all ins in dict
        radio_groups = []
        for i in radio_raw:
            radio_groups.append(i)

        embed_name = 'Радиостанции'

        class PreviousButton(Button):
            def __init__(self):
                super().__init__(label="<<", custom_id="previous")

            async def callback(self, interaction: Interaction):
                view = self.view
                view.current_page = max(0, view.current_page - 1)
                embed = view.embeds[view.current_page]
                embed.title = f"{embed_name} "\
                    + f"[{view.current_page + 1}/{len(view.embeds)}]"
                await interaction.response.edit_message(embed=embed, view=view)

        class NextButton(Button):
            def __init__(self):
                super().__init__(label=">>", custom_id="next")

            async def callback(self, interaction: Interaction):
                view = self.view
                view.current_page = min(
                    len(view.embeds) - 1, view.current_page + 1)
                embed = view.embeds[view.current_page]
                embed.title = f"{embed_name} "\
                    + f"[{view.current_page + 1}/{len(view.embeds)}]"
                await interaction.response.edit_message(embed=embed, view=view)

        class RadioMenu(View):
            def __init__(self, ctx, embeds):
                super().__init__()
                self.ctx = ctx
                self.embeds = embeds
                self.current_page = 0
                self.message = None

                self.add_item(PreviousButton())
                self.add_item(NextButton())

            async def interaction_check(self, interaction: Interaction) -> bool:
                return interaction.user == self.ctx.author

            async def start(self):
                embed = self.embeds[self.current_page]
                embed.title = f"{embed_name} "\
                    + f"[{self.current_page + 1}/{len(self.embeds)}]"
                self.message = await self.ctx.send(embed=embed, view=self)

        # In your command
        embeds = []
        embed = Embed(color=EMBED_COLOR)
        station_count = 0
        for group in radio_groups:
            # Sort stations in each group alphabetically
            sorted_stations = sorted(
                radio_raw[group].items(), key=lambda x: x[1]['name'])
            for station, station_info in sorted_stations:
                if station_count == 10:
                    embeds.append(embed)
                    embed = Embed(color=EMBED_COLOR)
                    station_count = 0
                station_info_str = '__**' + \
                    station_info['name'] + '**__' + \
                    ': ' + station_info['desc'] + '\n'
                embed.add_field(name='', value=station_info_str, inline=False)
                station_count += 1
        if station_count > 0:
            embeds.append(embed)
        menu = RadioMenu(ctx, embeds)
        await menu.start()

    @commands.command(name="radio", description="Подключиться к радиостанции")
    async def radio(self, ctx: commands.Context, name):
        """
        - Подключиться к радиостанции

        Parameters
        ----------
        ctx : commands.Context
            The context object.
        name : str
            - Название радиостанции
        """

        if ctx.author.voice.channel:
            if not ctx.guild.voice_client:
                player = await ctx.author.voice.channel.connect()
            else:
                player = ctx.guild.voice_client
            await ctx.guild.change_voice_state(channel=ctx.guild.voice_client.channel, self_mute=False, self_deaf=True)

            radio_raw = urls.radio
            # find all ins in dict
            radio_groups = []
            radios = {}
            for group in radio_raw:
                radio_groups.append(group)
                for radio in radio_raw[group]:
                    radios[radio_raw[group][radio]['name']
                           ] = radio_raw[group][radio]
            # use Levenshtein distance to find the closest match
            closest_match = ''
            closest_match_ratio = -9999999999
            for station in radios:
                ratio = Levenshtein.ratio(station.lower(), name.lower())
                if ratio > closest_match_ratio:
                    closest_match_ratio = ratio
                    closest_match = station
            if closest_match_ratio == 0:
                # pick random
                closest_match = random.choice(list(radios.keys()))
            name = closest_match

            def get_probability_msg(ratio):
                if ratio >= 0.99:
                    return "вы же ввели запрос точно как название радиостанции... удивительно..."
                elif ratio >= 0.9:
                    return "да, да! это то, что вы искали"
                elif ratio >= 0.8:
                    return "да, это то, что вы искали"
                elif ratio >= 0.7:
                    return "да, это то, что вы искали, но пишите точнее"
                elif ratio >= 0.6:
                    return "надеюсь, это то, что вы искали"
                elif ratio >= 0.5:
                    return "если это не то, что вы искали, то что же тогда? :sob:"
                elif ratio >= 0.4:
                    return "если я не ошибаюсь, то это то, что вы искали"
                elif ratio >= 0.3:
                    return "это не то, что вы искали, но похоже на то"
                elif ratio >= 0.2:
                    return "сомневаюсь, что это то, что вы искали"
                else:
                    return "это определенно не то, что вы искали, но лучше, чем ничего..."

            embed = discord.Embed(title="Играет радио",
                                  description=f"\"__**{name}**__\"\n"
                                  + get_probability_msg(closest_match_ratio), color=EMBED_COLOR)
            stopped_embed = discord.Embed(title="Играло радио",
                                          description=f"\"__**{name}**__\"\n"
                                          + get_probability_msg(closest_match_ratio), color=EMBED_COLOR)

            voice_client = ctx.voice_client

            stop_button = discord.ui.Button(
                style=discord.ButtonStyle.danger, label="Stop")
            # if voice_client.is_playing():
            # voice_client.stop()

            async def callback_stop_button(interaction):
                if voice_client.is_playing():
                    voice_client.stop()
                await interaction.response.edit_message(view=None, embed=stopped_embed)

            stop_button.callback = callback_stop_button

            view = discord.ui.View()
            view.add_item(stop_button)

            # destroy the view if stopped playing

            msg = await ctx.send(embed=embed, view=view, mention_author=True)

            if voice_client.is_playing():
                voice_client.stop()

            player.play(discord.FFmpegPCMAudio(
                radios[name]['url'], **FFMPEG_OPTIONS))
            playing = player.is_playing()
            await asyncio.sleep(5)
            await ctx.message.delete()
            while playing:
                await asyncio.sleep(1)
                playing = player.is_playing()

            await msg.edit(view=None, embed=stopped_embed)
            await asyncio.sleep(10)
            await msg.delete()
        else:
            await ctx.send("Пожалуйста, подключитесь к голосовому каналу")


async def setup(bot):
    await bot.add_cog(Player(bot))

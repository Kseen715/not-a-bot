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

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
EMBED_COLOR = 0x9b111e


class Urls:
    def __init__(self):
        self.radio = json.load(open("cogs/radio.json", "r", encoding="utf-8"))


urls = Urls()


class Player(commands.Cog):
    __init__: commands.Bot

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="play", description="Воспроизвести трек (YouTube)")
    async def play(self, ctx: commands.Context, url):
        """
        - Воспроизвести трек

        Parameters
        ----------
        ctx : commands.Context
            The context object.
        url : str
            - Ссылка на трек (YouTube)
        """

        if ctx.author.voice.channel:
            if not ctx.guild.voice_client:
                player = await ctx.author.voice.channel.connect()
            else:
                player = ctx.guild.voice_client
            await ctx.guild.change_voice_state(channel=ctx.guild.voice_client.channel, self_mute=False, self_deaf=True)
            yt = YouTube(url)
            audio = yt.streams.filter(only_audio=True).first()
            name = yt.title
            if player.is_playing():
                player.stop()

            embed = discord.Embed(title="Играет трек",
                                  description=f"\"__**{name}**__\"", color=EMBED_COLOR)

            msg = await ctx.send(embed=embed, reference=ctx.message, mention_author=True)
            player.play(discord.FFmpegPCMAudio(
                audio.url, **FFMPEG_OPTIONS))
            playing = player.is_playing()
            await asyncio.sleep(5)
            await ctx.message.delete()
            while playing:
                await asyncio.sleep(1)
                playing = player.is_playing()

            await asyncio.sleep(10)
            await msg.delete()
        else:
            await ctx.send("Пожалуйста, подключитесь к голосовому каналу.")

    @commands.command(name="stop", description="Остановить воспроизведение")
    async def stop(self, ctx: commands.Context):
        """
        - Остановить воспроизведение

        Parameters
        ----------
        ctx : commands.Context
            The context object.
        """
        await ctx.send("Воспроизведение остановлено", delete_after=5, reference=ctx.message)
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

            msg = await ctx.send(embed=embed, view=view, reference=ctx.message, mention_author=True)

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

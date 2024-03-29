import datetime
import logging
import os
import traceback
import typing

import aiohttp
import asyncio
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv


class NAB(commands.Bot):
    client: aiohttp.ClientSession
    _uptime: datetime.datetime = datetime.datetime.utcnow()

    def __init__(self, ext_dir: str, *args: typing.Any, **kwargs: typing.Any) -> None:
        intents = discord.Intents.all()
        intents.members = True
        intents.message_content = True
        __prefix = os.getenv("PREFIX")
        super().__init__(*args, **kwargs,
                         command_prefix=commands.when_mentioned_or(__prefix), intents=intents)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.ext_dir = ext_dir
        self.synced = False
        # set presence
        self.activity = discord.Activity(
            type=discord.ActivityType.listening, name="@N-A-B help")

    async def _load_extensions(self) -> None:
        if not os.path.isdir(self.ext_dir):
            self.logger\
                .error(f"Extension directory {self.ext_dir} does not exist.")
            return
        for filename in os.listdir(self.ext_dir):
            if filename.endswith(".py") and not filename.startswith("_"):
                try:
                    await self.load_extension(f"{self.ext_dir}.{filename[:-3]}")
                    self.logger.info(f"Loaded extension {filename[:-3]}")
                except commands.ExtensionError:
                    self.logger\
                        .error(f"Failed to load extension {filename[:-3]}\n"
                               + f"{traceback.format_exc()}")

    async def on_error(self, event_method: str, *args: typing.Any, **kwargs: typing.Any) -> None:
        self.logger\
            .error(f"An error occurred in {event_method}.\n"
                   + f"{traceback.format_exc()}")

    async def on_ready(self) -> None:
        self.logger.info(f"Logged in as {self.user} ({self.user.id})")

    async def setup_hook(self) -> None:
        self.client = aiohttp.ClientSession()

        await self._load_extensions()
        if not self.synced:
            await self.tree.sync()
            self.synced = not self.synced
            self.logger.info("Synced command tree")

    async def close(self) -> None:
        await super().close()
        await self.client.close()

    async def load_cogs(self):
        await self._load_extensions()

    def run(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        load_dotenv()
        try:
            # asyncio.run(self.load_cogs())
            super().run(str(os.getenv("TOKEN")), *args, **kwargs)
        except (discord.LoginFailure, KeyboardInterrupt):
            self.logger.info("Exiting...")
            exit()

    @property
    def user(self) -> discord.ClientUser:
        assert super().user, "Bot is not ready yet"
        return typing.cast(discord.ClientUser, super().user)

    @property
    def uptime(self) -> datetime.timedelta:
        return datetime.datetime.utcnow() - self._uptime


def main() -> None:
    try:
        logging.basicConfig(level=logging.INFO,
                            format="[%(asctime)s] %(levelname)s: %(message)s")
        bot = NAB(ext_dir="cogs")

        bot.run()

    except KeyboardInterrupt:
        bot.logger.info("Exiting...")
        asyncio.run(bot.close())
        asyncio.run(asyncio.sleep(15))


if __name__ == "__main__":
    main()

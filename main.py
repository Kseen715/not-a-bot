import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")

bot = commands.Bot(command_prefix=commands.when_mentioned,
                   intents=discord.Intents.all())


async def setup_hook() -> None:
    # This function is automatically called before the bot starts
    await bot.tree.sync()

# Not the best way to sync slash commands, but it will have to do for now. A better way is to create a command that calls the sync function.
bot.setup_hook = setup_hook


@bot.tree.command()
async def ping(inter: discord.Interaction) -> None:
    await inter.response.send_message(f"> Pong! {round(bot.latency * 1000)}ms")


@bot.event
async def on_ready() -> None:
    print(f"Logged in as {bot.user}")


if __name__ == "__main__":
    bot.run(TOKEN)

from discord.ext import commands


class Ping(commands.Cog):
    __init__: commands.Bot

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="ping", description="Ping to the server")
    async def ping(self, ctx: commands.Context):
        """
        Ping to the server

        Parameters
        ----------
        ctx : commands.Context
            The context object.
        """
        await ctx.send(f"> Pong! {round(self.bot.latency * 1000)}ms")


async def setup(bot):
    await bot.add_cog(Ping(bot))

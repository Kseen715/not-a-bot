from discord.ext import commands
from datetime import datetime, timedelta


class Chat(commands.Cog):
    __init__: commands.Bot

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="prune", description="Clear messages")
    @commands.has_permissions(administrator=True)
    async def prune(self, ctx: commands.Context, amount: int):
        """
        - Удаление сообщений

        Parameters
        ----------
        ctx : commands.Context
            The context object.
        amount : int
            - Количество сообщений для удаления
        """
        # +1 to include the command message itself
        await ctx.channel.purge(limit=amount+1)

    @commands.command(name="prunetime", description="Clear messages")
    @commands.has_permissions(administrator=True)
    async def prunetime(self, ctx: commands.Context, time: str):
        """
        - Очистка сообщений за последнее время

        Parameters
        ----------
        ctx : commands.Context
            The context object.
        time : int
            - Время для удаления (пример: 1d2h3m4s)
        """
        # 365d23h59m59s is the maximum time, parse it to seconds
        time = time.replace("d", "*86400+").replace("h",
                                                    "*3600+").replace("m", "*60+").replace("s", "")
        if time[-1] == "+":
            time = time[:-1]
        # eval() is evil, but it's the only way to parse a string into a mathematical expression
        time = eval(time)

        # Calculate the datetime after which messages should be deleted
        delete_after = datetime.now() - timedelta(seconds=time)

        # +1 to include the command message itself
        await ctx.channel.purge(after=delete_after)  # time in seconds


async def setup(bot):
    await bot.add_cog(Chat(bot))

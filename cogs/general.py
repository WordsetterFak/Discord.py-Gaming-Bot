from discord.ext import commands
from discord.ext.commands import Context
from discord import Client, Embed, Colour


class GeneralCommandsCog(commands.Cog):
    """
    Commands that are not part of any game
    """

    def __init__(self, client: Client):
        self.client: Client = client

    @commands.command(aliases=["INFO", "iNFO", "Info"])
    async def info(self, ctx: Context):

        embed = Embed(
            title="About this Botℹ️",
            colour=Colour.teal()
        )

        embed.add_field(
            name="Text📝",
            value="This is an open source bot available at https://github.com/Wordsetter0/Discord.py-Gaming-Bot ,"
                  " created by Wordsetter#2167"
        )

        await ctx.reply(embed=embed)

    @commands.command(aliases=["credits"])
    async def contributors(self, ctx: Context):
        pass  # for contributors, etc

    @commands.command()
    async def helpmenu(self):
        pass

    @commands.command()
    async def ping(self, ctx: Context):
        await ctx.reply(f"**Latency: {round(self.client.latency * 1000)} ms**")


def setup(client):
    client.add_cog(GeneralCommandsCog(client))

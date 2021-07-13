from discord.ext import commands
from discord.ext.commands import Context
from discord import Client


class BattleshipCog(commands.Cog):

    def __init__(self, client: Client):
        self.client: Client = client


def setup(client):
    client.add_cog(BattleshipCog(client))

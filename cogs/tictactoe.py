from discord.ext import commands
from discord.ext.commands import Context
from discord import Client, User, Embed, Colour
import classes.games.TicTacToe as tic


class TicTacToeGameCog(commands.Cog):

    _channel_to_game: dict[str, tic.TicTacToeGame] = {}

    def __init__(self, client: Client):
        self.client: Client = client


def setup(client):
    client.add_cog(TicTacToeGameCog(client))

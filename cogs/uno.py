from discord.ext import commands
from discord.ext.commands import Context
from discord import Client, User
from classes.games.Uno import UnoGame
from classes.Player import Player


class UnoGameCog(commands.Cog):  # this game is played in dms

    _player_to_game: dict = {}  # maps users to game

    def __init__(self, client: Client):
        self.client: Client = client

    @commands.command()
    async def uchallenge(self, ctx: Context, *users: User):
        pass

    @commands.command()
    async def d(self, ctx: Context):
        pass

    @classmethod
    async def delete_game(cls, game: UnoGame):

        for player in game.players:

            Player.occupied_players.remove(player.discord_id)
            del cls._player_to_game[str(player.discord_id)]

        del game


def setup(client):
    client.add_cog(UnoGameCog(client))

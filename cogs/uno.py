from discord.ext import commands
from discord.ext.commands import Context
from discord import Client, User, Embed, Colour
from classes.games.Uno import UnoGame, UnoPlayer
from classes.Player import Player
from classes.Game import Game
from time import time
import random
import asyncio


class UnoGameCog(commands.Cog):  # this game is played in dms with 2-4 players

    _player_to_game: dict = {}  # maps users to game

    def __init__(self, client: Client):
        self.client: Client = client

    @commands.command(aliases=["Uchallenge", "UCHALLENGE", "uCHALLENGE"])
    async def uchallenge(self, ctx: Context, *users: User):

        if ctx.guild is None:
            await ctx.reply("**You cannot challenge someone outside of a server**")
            return

        if ctx.channel.id in Game.occupied_channels:
            await ctx.author.send("**While UNO is played in dms, you need to challenge players in another channel, "
                                  f"since <#{ctx.channel}> is occupied by other players!**")
            return

        users = list(users)

        if len(users) > 4:
            users = users[0:5]

        for user in users:

            if user.id == ctx.author.id:

                users.remove(user)

            elif len([x for x in users if x.id == user.id]) > 1:

                users.remove(user)

            elif user.id in Player.occupied_players:

                users.remove(user)

        users.append(ctx.author)

        if len(users) < 2:
            await ctx.reply("**Not enough players challenged/available for a game of UNO!**")
            return

        embed = Embed(
            title="Uno In-Game Commands📝",
            colour=random.choice([Colour.red(), Colour.green(), Colour.gold(), Colour.blue()])
        )

        embed.add_field(
            name="Commands ⚙️",
            value=" "
        )

        message = await ctx.send(
            f"{ctx.author.mention} has challenged {', '.join(x.mention for x in users)} to a game of UNO,"
            f" will they accept?"
        )

        reactions = ["✅", "❌"]
        accepted_users = []

        for reaction in reactions:
            await message.add_reaction(reaction)

        def check(react, author):
            return author in users and str(react.emoji) in reactions

        while True:
            try:

                reaction, user = await self.client.wait_for("reaction_add", timeout=30, check=check)

                if str(reaction.emoji) == "✅":

                    if user.id not in [x.id for x in accepted_users]:
                        accepted_users.append(user)

                    if len(accepted_users) == len(users):
                        break

                elif str(reaction.emoji) == "❌":

                    if user.id in [x.id for x in accepted_users]:
                        accepted_users.remove(user)

                    accepted_users.append(user)

                    if len(accepted_users) == len(users):
                        break

            except asyncio.TimeoutError:
                break

        for user in accepted_users:

            if user.id in Player.occupied_players:

                await ctx.send(f"**{user.mention} joined another game!**")
                accepted_users.remove(user)

        if len(users) < 2:
            await ctx.reply("**Not enough players were gathered for a game of UNO!**")
            return

        for user in accepted_users:

            Player.occupied_players.append(user.id)

        uno_players = []

        for user in accepted_users:

            await user.send(content="**Game beginning soon!**", embed=embed)
            uno_players.append(UnoPlayer(user.id, user))

        game = UnoGame(uno_players)

        for player in uno_players:
            self._player_to_game[str(player.discord_id)] = game

        await asyncio.sleep(3)

        game.timer = time()
        game.ongoing = True
        game.begin_game()

        await self.display(game)

    @commands.command()
    async def d(self, ctx: Context):
        pass

    @classmethod
    async def display(cls, game: UnoGame):

        for player in game.players:

            card_display = "\n".join([x.display() for x in player.hand])  # TODO

    @classmethod
    async def delete_game(cls, game: UnoGame):

        for player in game.players:

            Player.occupied_players.remove(player.discord_id)
            del cls._player_to_game[str(player.discord_id)]

        del game


def setup(client):
    client.add_cog(UnoGameCog(client))

from discord.ext import commands
from discord.ext.commands import Context
from discord import Client, User, Embed, Colour
from classes.Player import Player
from classes.Game import Game
from classes.games.BattleshipsGame import BattleshipsGame, BattleshipsPlayer
import asyncio


class BattleshipsCog(commands.Cog):

    _player_to_game: dict = {}  # allows player to change fleet in dms
    _channel_to_game: dict = {}

    def __init__(self, client: Client):
        self.client: Client = client

    @commands.command(aliases=["Bchallenge", "BCHALLENGE", "bCHALLENGE"])
    async def bchallenge(self, ctx: Context, user: User):

        if ctx.guild is None:
            await ctx.reply("**You cannot challenge someone outside of a server**")
            return

        if ctx.channel.id in Game.occupied_channels:
            await ctx.reply("**This channel is occupied!**")
            return

        if ctx.author.id in Player.occupied_players:
            await ctx.reply("**You are already in a game!**")
            return

        if user.id in Player.occupied_players:
            await ctx.reply(f"**{user.mention} is in another game!**")
            return

        embed = Embed(
            title="Battleships In-Game Commands📝",
            color=Colour.dark_blue()
        )

        message = await ctx.send(
            content=f"**{ctx.author.mention} has challenged {user.mention} to a game of Battleships,"
                    f" will he accept?**",
            embed=embed
        )

        reactions = ["✅", "❌"]
        accepted = False

        for reaction in reactions:
            await message.add_reaction(reaction)

        def check(react, author):
            return author == user and str(react.emoji) in reactions

        while True:
            try:

                reaction, user = await self.client.wait_for("reaction_add", timeout=30, check=check)

                if str(reaction.emoji) == "✅":
                    accepted = True
                    break
                elif str(reaction.emoji) == "❌":
                    break

            except asyncio.TimeoutError:
                break

        if accepted:

            if ctx.channel.id in Game.occupied_channels:
                await ctx.reply("**This channel was occupied, before the challenge was accepted!**")
                return

            if ctx.author.id in Player.occupied_players:
                await ctx.reply("**You joined a game, before the challenge was accepted!**")
                return

            if user.id in Player.occupied_players:
                await ctx.reply(f"**{user.mention} joined a game, before the challenge was accepted!**")
                return

            Player.occupied_players.append(user.id)
            Player.occupied_players.append(ctx.author.id)
            Game.occupied_channels.append(ctx.channel.id)

            game = BattleshipsGame([ctx.author.id, user.id])
            self._channel_to_game[str(ctx.channel.id)] = game
            self._player_to_game[str(ctx.author.id)] = game
            self._player_to_game[str(user.id)] = game

        else:

            await ctx.reply(f"**{user.mention} turned down/did not respond the challenge!**")


def setup(client):
    client.add_cog(BattleshipsCog(client))

from discord.ext import commands
from discord.ext.commands import Context
from discord import Client, User, Embed, Colour
from classes.Player import Player
from classes.Game import Game
from classes.games.Battleships import BattleshipsGame
from time import time
import asyncio


class BattleshipsCog(commands.Cog):

    _player_to_game: dict[str, BattleshipsGame] = {}  # allows player to change fleet in dms
    _channel_to_game: dict[str, BattleshipsGame] = {}

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

        embed = Embed(  # TODO
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

            await ctx.send(
                content=f"{ctx.author.mention}|{user.mention}\n"
                        f"**Game will begin in 20 seconds, in the meantime you can change your fleet up to 3 times,"
                        f" if you are not satisfied.**"
            )

            await asyncio.sleep(20)

            game.timer = time()
            game.ongoing = True

            await self.display(ctx, game)  # send the first message

        else:

            await ctx.reply(f"**{user.mention} turned down/did not respond the challenge!**")

    @commands.command(aliases=["S", "shoot", "SHOOT", "Shoot", "sHOOT"])
    async def s(self, pos: str):
        pass  # TODO

    @commands.command(aliases=["Breroll", "BREROLL", "bREROLL"])
    async def breroll(self, ctx: Context):

        try:

            game = self._player_to_game[str(ctx.author.id)]

        except KeyError:

            await ctx.reply("**You have not joined any Battleships game!**")
            return

        response = game.change_fleet(ctx.author.id)

        if response == -2:
            await ctx.reply("**Game is ongoing, you cannot change your fleet!**")
            return

        elif response == -1:
            await ctx.reply("**You have run out of rerolls!**")
            return

        display = game.display(ctx.author.id)

        await ctx.author.send(
            content=f"Reroll successful, you have {response} rerolls left!\n{display}"
        )

    @commands.command(aliases=["Timeout", "TIMEOUT", "tIMEOUT"])
    async def timeout(self, ctx: Context):

        try:  # TODO

            game = self._player_to_game[str(ctx.author.id)]

        except KeyError:

            await ctx.reply("**You have not joined any Battleships game!**")
            return

    @classmethod
    async def display(cls, ctx: Context, game: BattleshipsGame):

        fleet_dis = game.display()

        await ctx.send(
            content=f"Its <@!{game.next.discord_id}>'s turn!\n{fleet_dis}"
        )


def setup(client):
    client.add_cog(BattleshipsCog(client))

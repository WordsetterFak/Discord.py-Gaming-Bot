from discord.ext import commands
from discord.ext.commands import Context
from discord import Client, User, Embed, Colour
from classes.Player import Player
from classes.Game import Game
import classes.games.Battleships as bb
from time import time
from re import search as re_search
import asyncio


class BattleshipsGameCog(commands.Cog):

    _player_to_game: dict[str, bb.BattleshipsGame] = {}  # allows player to change fleet in dms
    _channel_to_game: dict[str, bb.BattleshipsGame] = {}

    def __init__(self, client: Client):
        self.client: Client = client

    @commands.command(aliases=["Bchallenge", "BCHALLENGE", "bCHALLENGE"])
    async def bchallenge(self, ctx: Context, user: User):

        if ctx.guild is None:
            await ctx.reply("**You cannot challenge someone outside of a server**")
            return

        if ctx.author.id == user.id:
            await ctx.reply("**You cannot challenge yourself!**")
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

            players = [ctx.author.id, user.id]

            game = bb.BattleshipsGame(players)

            Game.occupied_channels.append(ctx.channel.id)
            self._channel_to_game[str(ctx.channel.id)] = game

            for player in players:

                Player.occupied_players.append(player)
                self._player_to_game[str(player)] = game

                display = game.display(discord_id=player, view_opponent_fleet=False)

                player_discord = await self.client.fetch_user(player)

                await player_discord.send(
                    content=f"Your fleet!(3 rerolls available)\n{display}"
                )

            await ctx.send(
                content=f"{ctx.author.mention}|{user.mention}\n"
                        f"**Game will begin in 20 seconds, in the meantime you can change your fleet up to 3 times,"
                        f" if you are not satisfied with your current fleet.**"
            )

            await asyncio.sleep(20)

            game.timer = time()
            game.ongoing = True

            await self.display(ctx, game)  # send the first message

        else:

            await ctx.reply(f"**{user.mention} turned down/did not respond the challenge!**")

    @commands.command(aliases=["S", "shoot", "SHOOT", "Shoot", "sHOOT"])
    async def s(self, ctx: Context, pos: str):

        try:

            game = self._player_to_game[str(ctx.author.id)]

        except KeyError:

            await ctx.reply("**You have not joined any Battleships game!**")
            return

        pos = pos.lower()

        if ctx.author.id != game.next.discord_id:

            await ctx.reply("**It is not your turn!**")
            return

        elif len(pos) != 2:

            await ctx.reply("**Invalid coordinates(wrong size)\n"
                            "Example: a2**")
            return

        pattern1 = "[a-j]+[0-9]"
        pattern2 = "[0-9]+[a-j]"

        if re_search(pattern1, pos):

            row = pos[0]
            column = int(pos[1])

        elif re_search(pattern2, pos):

            row = pos[1]
            column = int(pos[0])

        else:

            await ctx.reply("**Invalid coordinates(wrong format)\n"
                            "Example: b6**")
            return

        hit, destroyed = game.shoot(row, column)

        if isinstance(hit, bb.Ship):

            if not destroyed:

                await ctx.reply(f"**You hit a ship:boom:**")

            else:

                await ctx.reply(f"**You sunk the {hit.name}({hit.size}):boom:**")

            if game.check_win():

                await self.conclude(ctx, game)

            else:

                game.next_round()

            await self.display(ctx, game)

        elif isinstance(hit, bb.Water):

            await ctx.reply(f"**You hit nothing:radio_button:**")

            game.next_round()

            await self.display(ctx, game)

        elif isinstance(hit, bb.ExplodedShip):

            await ctx.reply(f"**You hit {pos} before and hit a ship, please shoot a new square!**")

        else:

            await ctx.reply(f"**You hit {pos} before and hit nothing, please shoot a new square!**")

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
    async def btimeout(self, ctx: Context):

        try:  # TODO

            game = self._player_to_game[str(ctx.author.id)]

        except KeyError:

            await ctx.reply("**You have not joined any Battleships game!**")
            return

    @commands.command()
    async def myfleet(self, ctx: Context):

        try:  # TODO

            game = self._player_to_game[str(ctx.author.id)]

        except KeyError:

            await ctx.reply("**You have not joined any Battleships game!**")
            return

    @commands.command()
    async def bsurrender(self, ctx: Context):

        try:  # TODO

            game = self._player_to_game[str(ctx.author.id)]

        except KeyError:

            await ctx.reply("**You have not joined any Battleships game!**")
            return

    @commands.command()
    async def btie(self, ctx: Context):

        try:  # TODO

            game = self._player_to_game[str(ctx.author.id)]

        except KeyError:

            await ctx.reply("**You have not joined any Battleships game!**")
            return

    @classmethod
    async def display(cls, ctx: Context, game: bb.BattleshipsGame):

        fleet_dis = game.display()

        await ctx.send(
            content=f"**Its <@!{game.next.discord_id}>'s turn!(Opponent's fleet)**\n"
                    f"{fleet_dis}"
        )

    @classmethod
    async def conclude(cls, ctx: Context, game: bb.BattleshipsGame):
        print("Done")  # TODO


def setup(client):
    client.add_cog(BattleshipsGameCog(client))

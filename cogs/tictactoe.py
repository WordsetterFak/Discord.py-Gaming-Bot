from discord.ext import commands
from discord.ext.commands import Context
from discord import Client, User, Embed, Colour
import classes.games.TicTacToe as tic
from classes.Game import Game
from classes.Player import Player
from main import get_prefix
from time import time
import asyncio


class TicTacToeGameCog(commands.Cog):

    _channel_to_game: dict[str, tic.TicTacToeGame] = {}

    def __init__(self, client: Client):
        self.client: Client = client

    @commands.command()
    async def tchallenge(self, ctx: Context, user: User):

        if ctx.guild is None:
            await ctx.reply("**You cannot challenge someone outside of a server**")
            return

        if ctx.author.id == user.id:
            await ctx.reply("**You cannot challenge yourself!**")
            return

        if ctx.channel.id in Game.occupied_channels:
            await ctx.reply("**This channel is occupied, by another game!**")
            return

        if ctx.author.id in Player.occupied_players:
            await ctx.reply("**You are already in a game!**")
            return

        if user.id in Player.occupied_players:
            await ctx.reply(f"**{user.mention} is in another game!**")
            return

        embed = Embed(
            title="TicTacToe In-Game Commands📝",
            color=Colour.red()
        )

        prefix = get_prefix(self.client, ctx)

        embed.add_field(
            name="In-Game Commands ⚙️",
            value="f"
        )

        message = await ctx.send(
            content=f"**{ctx.author.mention} has challenged {user.mention} to a game of TicTacToe,"
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

            game = tic.TicTacToeGame(players)

            Game.occupied_channels.append(ctx.channel.id)
            self._channel_to_game[str(ctx.channel.id)] = game

            for player in players:

                Player.occupied_players.append(player)

            await ctx.send(
                content=f"**{ctx.author.mention} ⚔️ {user.mention}\n"
                        f"{game.get_player_by_id(ctx.author.id).emoji}{ctx.author.mention}\n"
                        f"{game.get_player_by_id(user.id).emoji}{user.mention}**"
            )

            await asyncio.sleep(1)

            game.timer = time()
            game.ongoing = True

            await self.display(ctx, game)  # send the first message

        else:

            await ctx.reply(f"**{user.mention} turned down/did not respond the challenge!**")

    @commands.command()
    async def place(self, ctx: Context, pos: int):
        pass  # TODO (left it here)

    @commands.command()
    async def tsurrender(self, ctx: Context):
        pass

    @commands.command()
    async def ttie(self, ctx: Context):
        pass

    @commands.command()
    async def ttimeout(self, ctx: Context):
        pass

    @classmethod
    async def display(cls, ctx: Context, game: tic.TicTacToeGame):
        txt = game.board.display()

        await ctx.send(f"**It is <@!{game.current_round_player.discord_id}>'s "
                       f"turn ({game.current_round_player.emoji})**\n")

        # these 2 messages are split, because discord will make emojis smaller when they are combined with normal text

        await ctx.send(txt)


def setup(client):
    client.add_cog(TicTacToeGameCog(client))

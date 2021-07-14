from discord.ext import commands
from discord.ext.commands import Context
from discord import Client, User, Embed, Colour
from classes.Player import Player
from classes.Game import Game
import classes.games.Battleships as bb
from main import get_prefix
from time import time
from re import search as re_search
import asyncio


class BattleshipsGameCog(commands.Cog):

    _player_to_game: dict[str, bb.BattleshipsGame] = {}  # allows player to use some commands outside the channel
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
            await ctx.reply("**This channel is occupied, by another game!**")
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

        prefix = get_prefix(self.client, ctx)

        embed.add_field(
            name="In-Game Commands ⚙️",
            value=f"**{prefix}bchallenge @user** (challenge someone to a battleships game)\n"
                  f"**{prefix}s pos** (fire your guns at pos) (Ex -> {prefix}s j6\n"
                  f"**{prefix}breroll** (change your fleet, up to 3 times)\n"
                  f"**{prefix}btimeout** (win, if your opponent has not played for more than 120 seconds)\n"
                  f"**{prefix}myfleet** (view your fleet)\n"
                  f"**{prefix}bsurrender** (surrender the game)\n"
                  f"**{prefix}btie** (propose a tie, if both of you agree the game ends in a tie)\n"
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
                    content=f"**Your fleet!(3 rerolls available)**\n{display}"
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

            game = self._channel_to_game[str(ctx.channel.id)]

            if ctx.author.id not in game.player_ids:

                await ctx.reply("**You are not part of this Battleships game!**")
                return

        except KeyError:

            await ctx.reply("**There is no Battleships game running in this channel!**")
            return

        if not game.ongoing:

            await ctx.reply("**Game has not yet started! Please wait**")
            return

        if ctx.author.id != game.current_round_player.discord_id:

            await ctx.reply("**It is not your turn!**")
            return

        elif len(pos) != 2:

            await ctx.reply("**Invalid coordinates(wrong size)\n"
                            "Example: a2**")
            return

        pos = pos.lower()

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

                await ctx.send(f"**Admiral:anchor: <@!{game.current_round_player.discord_id}>"
                               f" defeated admiral:anchor: <@!{game.next_player().discord_id}>!**")
                self.delete_game(ctx, game)

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
            content=f"**Reroll successful, you have {response} rerolls left!**\n{display}"
        )

    @commands.command(aliases=["Timeout", "TIMEOUT", "tIMEOUT"])
    async def btimeout(self, ctx: Context):

        try:

            game = self._channel_to_game[str(ctx.channel.id)]

            if ctx.author.id not in game.player_ids:

                await ctx.reply("**You are not part of this Battleships game!**")
                return

        except KeyError:

            await ctx.reply("**There is no Battleships game running in this channel!**")
            return

        if time() - game.timer > game.TIMEOUT:

            game.current_round_player = game.next_player()

            await ctx.send(f"**Admiral:anchor: <@!{game.current_round_player}> defeated "
                           f"admiral:anchor: <@!{game.next_player().discord_id}> due to "
                           f"the inactivity of the latter!**")

            self.delete_game(ctx, game)

    @commands.command(aliases=["Myfleet", "MYFLEET", "mYFLEET"])
    async def myfleet(self, ctx: Context):

        try:

            game = self._player_to_game[str(ctx.author.id)]

        except KeyError:

            await ctx.reply("**You have not joined any Battleships game!**")
            return

        fleet_dis = game.display(discord_id=ctx.author.id, view_opponent_fleet=False)

        await ctx.author.send(
            content=f"**Its <@!{game.current_round_player.discord_id}>'s turn!(Your fleet:anchor:)**\n"
                    f"{fleet_dis}"
        )

    @commands.command(aliases=["Bsurrender", "BSURRENDER", "bSURRENDER"])
    async def bsurrender(self, ctx: Context):

        try:

            game = self._channel_to_game[str(ctx.channel.id)]

            if ctx.author.id not in game.player_ids:
                await ctx.reply("**You are not part of this Battleships game!**")
                return

        except KeyError:

            await ctx.reply("**There is no Battleships game running in this channel!**")
            return

        game.ongoing = False

        defeated = game.get_player_by_id(ctx.author.id)
        winner = [x for x in game.player_ids if x != defeated.discord_id][0]

        await ctx.send(f"**Admiral:anchor:<@!{defeated.discord_id}> surrendered to admiral:anchor:<@!{winner}>**")

        self.delete_game(ctx, game)

    @commands.command(aliases=["Btie", "BTIE", "bTIE"])
    async def btie(self, ctx: Context):

        try:

            game = self._channel_to_game[str(ctx.channel.id)]

            if ctx.author.id not in game.player_ids:
                await ctx.reply("**You are not part of this Battleships game!**")
                return

        except KeyError:

            await ctx.reply("**There is no Battleships game running in this channel!**")
            return

        proposed_tie_player = game.get_player_by_id(ctx.author.id)
        other_player = [x for x in game.players if x.discord_id != ctx.author.id][0]

        proposed_tie_player.proposed_tie = True

        if proposed_tie_player.proposed_tie and other_player.proposed_tie:

            game.ongoing = False

            await ctx.send(f"**Admiral:anchor:<@!{proposed_tie_player.discord_id}> "
                           f"and admiral:anchor:<@!{proposed_tie_player.discord_id}>"
                           f" agreed to a tie!**")

            self.delete_game(ctx, game)

        else:

            await ctx.send(f"**{ctx.author.mention} proposed a tie to <@!{other_player.discord_id}>**")

    @classmethod
    async def display(cls, ctx: Context, game: bb.BattleshipsGame):

        fleet_dis = game.display()

        await ctx.send(
            content=f"**Its <@!{game.current_round_player.discord_id}>'s turn!(Opponent's fleet:crossed_swords:)**\n"
                    f"{fleet_dis}"
        )

    @classmethod
    def delete_game(cls, ctx: Context, game: bb.BattleshipsGame):

        Game.occupied_channels.remove(ctx.channel.id)
        del cls._channel_to_game[str(ctx.channel.id)]

        for player in game.players:

            Player.occupied_players.remove(player.discord_id)
            del cls._player_to_game[str(player.discord_id)]

        del game

    @bchallenge.error
    async def bchallenge_error(self, ctx: Context, error: Exception):

        prefix = get_prefix(self.client, ctx)

        if isinstance(error, commands.MissingRequiredArgument):

            await ctx.reply("**You need to specify the user!\n"
                            f"Example: {prefix}bchallenge @user**")

        elif isinstance(error, commands.UserNotFound):

            await ctx.reply("**User does not exist or could not be found!\n"
                            f"Example: {prefix}bchallenge @user**")

    @s.error
    async def s_error(self, ctx: Context, error: Exception):
        prefix = get_prefix(self.client, ctx)

        if isinstance(error, commands.MissingRequiredArgument):

            await ctx.reply("**You need to specify the coordinates!\n"
                            f"Example: {prefix}s c8**")


def setup(client):
    client.add_cog(BattleshipsGameCog(client))

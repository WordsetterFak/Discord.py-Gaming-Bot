from discord.ext import commands
from discord.ext.commands import Context
from discord import Client, User, Embed, Colour
from classes.games.Uno import UnoGame, UnoPlayer, all_cards, UnoCard
from classes.Player import Player
from classes.Game import Game
from time import time
import random
import asyncio


class UnoGameCog(commands.Cog):  # this game is played in dms with 2-4 players

    _player_to_game: dict[str, UnoGame] = {}  # maps users to game

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

            elif len([x for x in users if x.id == user.id]) > 1:  # duplicate players

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
        game.deal_cards()

        await self.display(game)

    @commands.command(aliases=["D", "drop", "DROP", "Drop", "dROP"])
    @commands.dm_only()
    async def d(self, ctx: Context, card_name: str, *args: str):

        if ctx.guild is not None:

            await ctx.reply("**Uno is played exclusively in dms!**")
            return

        try:

            game = self._player_to_game[str(ctx.author.id)]

        except KeyError:

            await ctx.reply("**You are not part of any UNO game!**")
            return

        if not game.ongoing:

            await ctx.reply("**Game has not started yet!**")
            return

        card_name = card_name.lower()
        current_player = game.current_player()

        if ctx.author.id != current_player.discord_id:

            await ctx.reply("**It's not your turn!**")
            return

        try:

            card = all_cards[card_name]

        except KeyError:

            await ctx.reply(f"**{card_name} does not exist!**\n"
                            f"(Look at the parenthesis of your desired card in your deck to find the correct name)\n")
            return

        if card not in all_cards:  # needs testing, might not yield the specified result

            await ctx.reply(f"**{card_name} is not in your hand!**\n")
            return

        averted_plus2 = False  # if there is a +x on the player and he plays a +2 then it goes to the next one
        original_cards_to_pickup = game.card_pickups  # to avoid giving +4 to yourself after playing +4
        success = False
        next_step = 1
        color_change = False

        if not card.special:  # normal numbered cards

            if card.color == game.last_card.color or card.number == game.last_card.number:

                success = True

        elif card.color != "black":  # action cards

            if card.symbol == "<>":

                if game.last_card.symbol == "<>" or game.last_card.color == card.color:

                    success = True
                    game.movement *= -1

            elif card.symbol == "X":

                if game.last_card.symbol == "X" or game.last_card.color == card.color:

                    success = True
                    next_step = 2

            elif card.symbol == "+2":

                if game.last_card.symbol == "+2" or game.last_card.color == card.color:

                    success = True
                    game.card_pickups += 2
                    averted_plus2 = True

        else:  # wild cards

            if game.last_card.color != "black":

                if card.name == "+4":

                    success = True
                    game.card_pickups += 4
                    color_change = True

                elif card.name == "cc":

                    success = True
                    color_change = True

        if color_change:

            if len(args) == 0:

                await ctx.reply("**When dropping a +4 card or a Colour Change card, you need to specify the color"
                                "(red, blue, yellow, green)\n**"
                                "Example: !d +4 g\n")
                return

            colors: dict[str, tuple] = {
                "red": ("red", "r", "re"), "blue": ("blue", "b", "bl", "blu"),
                "yellow": ("yellow", "yello", "yell", "y", "yel", "ye"),
                "green": ("g", "gr", "gre", "gree", "green")
            }

            requested_color = args[0].lower()
            color = "null"

            for k, v in colors.items():

                if requested_color in v:

                    color = k
                    break

            if color == "null":

                await ctx.reply(f"**Color {requested_color} does not exist!**\n"
                                f"Valid colors: (red, blue, yellow, green)")
                return

            game.last_card = all_cards[f"{color}{card.symbol}"]

        if not success:

            await ctx.reply(f"**You cannot play {card.display()} on top of {game.last_card.display()}**")
            return

        else:

            game.last_card = card
            current_player.hand.remove(card)

        if game.card_pickups > 0:

            if not averted_plus2 and original_cards_to_pickup != 0:

                cards_to_pickup = game.card_pickups - (game.card_pickups - original_cards_to_pickup)

                if cards_to_pickup != 0:

                    picked_up_cards = []

                    for _ in range(cards_to_pickup):

                        pickup_card = game.take_card()
                        picked_up_cards.append(pickup_card)
                        current_player.hand.append(pickup_card)

                    picked_up_cards = "\n".join([x.display() for x in picked_up_cards])

                    await current_player.discord_user.send(
                        f"**You picked up {cards_to_pickup} cards:**\n"
                        f"{picked_up_cards}"
                    )

                    game.card_pickups -= cards_to_pickup

        if len(current_player.hand) == 0:

            print(f"Victory detected, winner: {current_player.discord_user}")  # testing purposes

        elif len(current_player.hand) == 1:

            for player in game.players:

                if player.discord_id != current_player.discord_id:

                    await player.discord_user.send(
                        f"**{current_player.discord_user.mention} has 1 card left! (UNO)**"
                    )

        else:

            if next_step > 1:

                await game.players[game.step_to_player(1)].discord_user.send(
                    f"**Your turn was skipped!**"
                )

            game.next_round(steps=next_step)
            await self.display(game)

    @commands.command(aliases=["pass", "PASS", "pASS"])
    @commands.dm_only()
    async def Pass(self, ctx: Context):  # Upper case P used, since pass cannot be used as a function name

        if ctx.guild is not None:

            await ctx.reply("**Uno is played exclusively in dms!**")
            return

        try:

            game = self._player_to_game[str(ctx.author.id)]

        except KeyError:

            await ctx.reply("**You are not part of any UNO game!**")
            return

        if not game.ongoing:

            await ctx.reply("**Game has not started yet!**")
            return

        current_player = game.current_player()

        if ctx.author.id != current_player.discord_id:

            await ctx.reply("**It's not your turn!**")
            return

        if len(current_player.hand) < 20:

            current_player.hand.append(game.take_card())
            game.next_round()
            await self.display(game)

        else:

            await ctx.reply("**Your turn was skipped, but you did not pick a card (You have too many)**")

    @commands.command()
    @commands.dm_only()
    async def utie(self):
        pass

    @commands.command()
    @commands.dm_only()
    async def usurrender(self):
        pass  # TODO add all surrender and timeout commands to a group

    @commands.command()
    @commands.dm_only()
    async def utimeout(self):
        pass

    @classmethod
    async def display(cls, game: UnoGame):
        queue = game.get_queue()

        for player in game.players:

            card_display = "\n".join([x.display() for x in player.hand])
            queue_display = ""
            cards_remaining_display = ""  # displays every player and his number of remaining cards

            for i in queue:

                if i.discord_id == player.discord_id:

                    queue_display += "**You**\n"
                    cards_remaining_display += f"**You: {len(i.hand)}**"
                    continue

                queue_display += f"{i.discord_user}\n"
                cards_remaining_display += f"{i.discord_user}: {len(i.hand)}"

            await player.discord_user.send(
                content=f"**It's {game.current_player().discord_user.mention}'s turn!**\n"
                        f"**Last Card Dropped: ({game.last_card.display()})**\n"
                        f"{game.last_card.image}\n"
                        f"------------\n"
                        f"**Cards**🎴\n"
                        f"{card_display}\n"
                        f"------------\n"
                        f"**Queue**♻️\n"
                        f"{queue_display}\n"
                        f"------------\n"
                        f"**Cards Remaining**\n"
                        f"{cards_remaining_display}\n"
            )

        if game.card_pickups > 0:

            await game.current_player().discord_user.send(
                f"**If you don't play a +2, you will draw {game.card_pickups} cards**"
            )

    @classmethod
    async def delete_game(cls, game: UnoGame):

        for player in game.players:

            Player.occupied_players.remove(player.discord_id)
            del cls._player_to_game[str(player.discord_id)]

        del game


def setup(client):
    client.add_cog(UnoGameCog(client))

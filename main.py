from discord.ext.commands.context import Context
from discord.ext.commands import has_permissions
from discord.ext import commands
from os import listdir
from discord import Guild, Embed, Colour
import json


TOKEN = open("TOKEN.txt", "r").read()  # discord bot TOKEN goes here


def get_prefix(bot_obj, message: Context) -> str:

    try:

        with open("bot/prefixes.json", 'r') as f:
            prefixes = json.load(f)

        return prefixes[str(message.guild.id)]

    except AttributeError:

        return "!"

    except KeyError:

        return "!"


client = commands.Bot(command_prefix=get_prefix)

for filename in listdir("cogs"):  # load all cogs/extensions

    if filename.endswith(".py"):

        client.load_extension(f"cogs.{filename[:-3]}")


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")


@client.event
async def on_command_error(ctx: Context, error: Exception):

    if isinstance(error, commands.CommandNotFound):

        await ctx.reply(f"**This command does not exist!**")


@client.event
async def on_guild_join(guild: Guild):

    with open("bot/prefixes.json", 'r') as f:
        prefixes = json.load(f)

    prefixes[str(guild.id)] = "!"

    with open("bot/prefixes.json", 'w') as f:
        json.dump(prefixes, f, indent=4)


@client.event
async def on_guild_remove(guild: Guild):

    with open("bot/prefixes.json", 'r') as f:
        prefixes = json.load(f)

    prefixes.pop(str(guild.id))

    with open("bot/prefixes.json", 'w') as f:
        json.dump(prefixes, f, indent=4)


@client.command(aliases=["PREFIX", "Prefix", "pREFIX"])
@has_permissions(administrator=True)
async def prefix(ctx: Context, new_prefix: str):

    if ctx.guild is None:

        await ctx.reply("**You cannot change the prefix outside of a server!**")
        return

    with open("bot/prefixes.json", 'r') as f:
        prefixes = json.load(f)

    prefixes[str(ctx.guild.id)] = new_prefix

    with open("bot/prefixes.json", 'w') as f:
        json.dump(prefixes, f, indent=4)

    await ctx.send(f"**Prefix changed to {new_prefix}**")


@prefix.error
async def prefix_error(ctx: Context, error: Exception):

    await ctx.reply("**Incorrect usage!\n"
                    f"Example: {get_prefix(client, ctx)}prefix .**")


@client.command(aliases=["INFO", "iNFO", "Info"])
async def info(ctx: Context):

    embed = Embed(
        title="About this Botℹ️",
        colour=Colour.teal()
    )

    embed.add_field(
        name="Text📝",
        value="This is an open source bot available at https://github.com/Wordsetter0/Discord.py-Gaming-Bot ,"
              " created by Wordsetter(WIP)"
    )

    await ctx.reply(embed=embed)


@client.command(aliases=["credits"])
async def bot_credits(ctx: Context):
    pass


@client.command()
async def ping(ctx: Context):
    await ctx.reply(f"**Latency: {round(client.latency * 1000)} ms**")


client.run(TOKEN)  # bot loop

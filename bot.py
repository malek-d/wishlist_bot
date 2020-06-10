import os,discord
from  config.EnvironmentCfg import getDiscordToken
from discord.ext import commands

client = commands.Bot(command_prefix = '$')

@client.command()
async def load(ctx, extension):
    client.load_extension('cogs.{0}'.format(extension))

@client.command()
async def unload(ctx, extension):
    client.unload_extension('cogs.{0}'.format(extension))

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')
client.run(getDiscordToken())
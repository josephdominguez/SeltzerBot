import os
import asyncpg
import discord
from discord.ext import commands

POSTGRES_HOST = os.getenv('POSTGRES_HOST')
POSTGRES_DB = os.getenv('POSTGRES_DB')
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')

DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')

credentials = {'user': POSTGRES_USER, 'password': POSTGRES_PASSWORD, 
               'database': POSTGRES_DB, 'host': POSTGRES_HOST}

bot = commands.Bot(command_prefix='.', description='', pm_help = False)

async def async_init():
    bot.pool = await asyncpg.create_pool(**credentials)
bot.loop.create_task(async_init())

extensions = ['cogs.lastfm', 'cogs.rym', 'cogs.youtube']

if __name__ == '__main__':
    for extension in extensions:
        bot.load_extension(extension)

@bot.event
async def on_ready():
    #check_servers()
    game = discord.Game('human cannonball')
    return await bot.change_presence(activity=discord.Game(name=game))

def check_servers():
    servers = bot.guilds
    print("connected to " + str(len(servers)))
    members = 0
    for server in servers:
        members += len(server.members)
        print(str(server) + " " + str(len(server.members)))
    print("total members = " + str(members))

bot.run(DISCORD_BOT_TOKEN)
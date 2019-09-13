import os
import discord
from discord.ext import commands
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

class YouTube(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def yt(self, ctx, *query):
        youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=GOOGLE_API_KEY)
        q = ' '.join(map(str, query))
        try:
            search_response = youtube.search().list(part='id,snippet', q=q, maxResults=10).execute()
        except HttpError:
            return await ctx.send('API quota reached. Try again later.')
        if len(search_response.get('items')):
            for item in search_response.get('items'):
                if item['id']['kind'] == 'youtube#video':
                    return await ctx.send(('https://www.youtube.com/watch?v={}').format(item['id']['videoId']))                    
        return await ctx.send('Could not find video.')

def setup(bot):
    bot.add_cog(YouTube(bot))
import os
import discord
from discord.ext import commands
import pylast

LASTFM_API_KEY = os.getenv('LASTFM_API_KEY')
LASTFM_API_SECRET = os.getenv('LASTFM_API_SECRET')
DEFAULT_AVATAR_URL = 'https://lastfm-img2.akamaized.net/i/u/avatar170s/818148bf682d429dc215c1705eb27b98'

network = pylast.LastFMNetwork(api_key=LASTFM_API_KEY, api_secret=LASTFM_API_SECRET)

class LastFM(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_fm_username(self, ctx):
        q = 'SELECT fm_username FROM fm_usernames WHERE discord_id = $1;'
        fm_username = await self.bot.pool.fetchrow(q, ctx.author.id)
        return fm_username['fm_username'] if fm_username else None

    @commands.group(pass_context=True, invoke_without_command=True)
    async def fm(self, ctx, username=None):
        fm_username = username if username else await self.get_fm_username(ctx)
        
        if not fm_username:
            return await ctx.send('Username not set. Try .fm set [username].')

        user = network.get_user(fm_username)
        
        try:
            user_avatar = user.get_image()
        except:
            return await ctx.send(('User {} not found.').format(fm_username))
        
        if not user_avatar: 
            user_avatar = DEFAULT_AVATAR_URL

        recent_tracks = []
        recent_tracks = user.get_recent_tracks(3)

        now_playing = user.get_now_playing()
        if now_playing:
            recent_tracks.insert(0, now_playing)

        description = ''
        for i in range(0, len(recent_tracks) - 1):
            place = '**Current:** ' if i == 0 else '**Previous:** '
            
            track = recent_tracks[i] if i == 0 and now_playing else recent_tracks[i].track
            track_name = track.get_name()
            artist_name = track.get_artist().get_name()

            #album = track.get_album()
            #album_name = album.get_name()
                
            description += ('{} {} - {}\n'.format(place, artist_name, track_name))
            #description += ('{} {} - {} [{}]\n'.format(place, artist_name, track_name, album_name))
        
        title = '**LastFM Profile**'
        description += ('<http://last.fm/user/{}>'.format(user))
        colour = ctx.author.colour

        embed = discord.Embed(title=title, description=description, colour=colour)
        embed.set_thumbnail(url=user_avatar)

        await ctx.send(embed=embed)

    @fm.command(pass_context=True)
    async def set(self, ctx, fm_username=None):
        if not fm_username:
            return await ctx.send('No username provided.')
        conn = await self.bot.pool.acquire()
        async with conn.transaction():
            q = '''
                INSERT INTO fm_usernames (discord_id, fm_username)
                  VALUES ($1, $2)
                ON CONFLICT (discord_id)
                DO
                  UPDATE
                    SET fm_username = $2;'''
            await self.bot.pool.execute(q, ctx.author.id, fm_username)
        await self.bot.pool.release(conn)
        await ctx.send('LastFM username set to {}.'.format(fm_username))

    @commands.command()
    async def fmyt(self, ctx):
        fm_username = await self.get_fm_username(ctx)
        
        if not fm_username:
            return await ctx.send('Username not set. Try .fm set [username]')

        user = network.get_user(fm_username)

        try:
            track = user.get_now_playing()
        except:
            return await ctx.send(('User not found.').format(fm_username))

        if not track:
            track = (user.get_recent_tracks(1))[0].track

        track_name = track.get_name()
        artist_name = track.get_artist().get_name()

        q = ('{} {}'.format(artist_name, track_name))

        await ctx.invoke(self.bot.get_command('yt'), q)

def setup(bot):
    bot.add_cog(LastFM(bot))
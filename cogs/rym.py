import discord
from discord.ext import commands
import cssutils
import aiohttp
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

RYM_USER_PAGE_URL = 'https://rateyourmusic.com/~'
BLANK_IMAGE_URL = 'https://pbs.twimg.com/profile_images/425274582581264384/X3QXBN8C.jpeg'
RYM_STARS = {
    'No stars': '**(Wishlisted)**',
    '0.50 stars': '<:half_star:598656463510175784>',
    '1.00 stars': ':star:',
    '1.50 stars': ':star: <:half_star:598656463510175784>',
    '2.00 stars': ':star: :star:',
    '2.50 stars': ':star: :star: <:half_star:598656463510175784>',
    '3.00 stars': ':star: :star: :star:',
    '3.50 stars': ':star: :star: :star: <:half_star:598656463510175784>',
    '4.00 stars': ':star: :star: :star: :star:',
    '4.50 stars': ':star: :star: :star: :star: <:half_star:598656463510175784>',
    '5.00 stars': ':star: :star: :star: :star: :star:'
}

class RateYourMusic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ua = UserAgent()

    async def get_html(self, url):
        async with aiohttp.ClientSession(headers={'User-Agent': self.ua.random}) as session:
            async with session.get(url, proxy='http://49.51.68.122:1080') as r:
                return await r.text(), r.status

    async def get_rym_username(self, ctx):
        q = 'SELECT rym_username FROM rym_usernames WHERE discord_id = $1;'
        rym_username = await self.bot.pool.fetchrow(q, ctx.author.id)
        return rym_username['rym_username'] if rym_username else None

    async def get_rym_user(self, ctx, username):
        rym_user_url = RYM_USER_PAGE_URL + username

        r, status = await self.get_html(rym_user_url)
        if status != 200:
            if status == 404:
                return await ctx.send('User does not exist.')
            return await ctx.send('Could not connect to RYM.')
        rym_user = BeautifulSoup(r, 'lxml')

        title = '**Rateyourmusic**'

        description = rym_user_url + '\n\n Recents:\n'
    
        for rating in rym_user.find('div', id='musicrecent').find('table', class_='mbgen').find_all('tr'):
            try:
                stars = rating.find('td', class_='or_q_rating_date_s').find('img')['alt']
            except:
                stars = 'No stars'
            try:
                release = rating.find('td', class_='or_q_albumartist_td')
                release = '{} - {} {}'.format(release.find('a', class_='artist').text, release.find('a', class_='album').text, release.find('span', class_='smallgray').text)
            except:
                break
            description += '{} {}\n'.format(RYM_STARS[stars], release)

        colour = ctx.author.colour

        embed = discord.Embed(title=title, description=description, colour=colour)

        try:
            user_avatar = cssutils.parseStyle(rym_user.find(id='profile_image')['style'])
            user_avatar = user_avatar['background-image'].replace('url(','').replace(')','')
            user_avatar = 'https:' + user_avatar
        except:
            user_avatar = BLANK_IMAGE_URL
        
        embed.set_thumbnail(url=user_avatar)

        await ctx.send(embed=embed)

    async def get_release(self, ctx, release):
        r, status = await self.get_html(release)
        if status != 200:
            if status == 404:
                return await ctx.send('Release does not exist.')
            return await ctx.send('Could not connect to RYM.')
        rym_release = BeautifulSoup(r, 'lxml')

        if rym_release.text == '404: File not found':
            return await ctx.send('No release found.')

        artist_name = rym_release.find('a', class_='artist').text
        album_name = rym_release.find('div', class_='album_title').contents[0].strip()
        release_type = rym_release.find('th', class_='info_hdr', text='Type').find_next_sibling().text

        try: 
            description = 'Released: ' + rym_release.find('th', class_='info_hdr', text='Released').find_next_sibling().text
        except:
            description = 'Released: '
        try:
            description += '\nRYM Rating: ' + rym_release.find('th', class_='info_hdr', text='RYM Rating').find_next_sibling().text.replace('\n', '')
        except:
            description += '\nRYM Rating: '
        try: 
            description += '\nRanked: ' + rym_release.find('th', class_='info_hdr', text='Ranked').find_next_sibling().text
        except:
            pass
        
        genres = rym_release.find('tr', class_='release_genres').find('td').text
        description += '\n\nGenres: ' + genres if genres.strip() != '' else ''
    
        descriptors = rym_release.find('tr', class_='release_descriptors').find('td').text
        description += 'Descriptiors: ' + descriptors if descriptors.strip() != '' else ''
        
        title = '**{} - {} [{}]**'.format(artist_name, album_name, release_type)
        description += release
        colour = ctx.author.colour

        embed = discord.Embed(title=title, description=description, colour=colour)

        try:
            release_art = 'https:' + rym_release.find('img', class_='coverart_img')['src']
        except:
            release_art = BLANK_IMAGE_URL
        embed.set_thumbnail(url=release_art)

        await ctx.send(embed=embed)

    async def get_film(self, ctx, film):
        r, status = await self.get_html(film)
        if status != 200:
            if status == 404:
                return await ctx.send('Release does not exist.')
            return await ctx.send('Could not connect to RYM.')
        rym_film = BeautifulSoup(r, 'lxml')

        if rym_film.text == '404: File not found':
            return await ctx.send('No film found.')

        film_title = rym_film.find('div', class_='film_title').contents[0].strip()

        try: 
            director = rym_film.find('th', class_='info_hdr', text='Directed by').find_next_sibling().text
        except:
            director = ''
        try: 
            description = 'Release date: ' + rym_film.find('th', class_='info_hdr', text='Release date').find_next_sibling().text
        except:
            description = 'Release date: '
        try:
            description += '\nRYM Rating: ' + rym_film.find('th', class_='info_hdr', text='RYM Rating').find_next_sibling().text.replace('\n', '')
        except:
            description += '\nRYM Rating: '
        try: 
            description += '\nRanked: ' + rym_film.find('th', class_='info_hdr', text='Ranked').find_next_sibling().text
        except:
            pass
        
        genres = rym_film.find('tr', class_='film_genres').find('td').text
        description += '\n\nGenres: ' + genres if genres.strip() != '' else ''
        
        title = '**{} - {}**'.format(director, film_title)
        description += film
        colour = ctx.author.colour

        embed = discord.Embed(title=title, description=description, colour=colour)

        try:
            film_art = 'https:' + rym_film.find('img', class_='coverart_img')['src']
        except:
            film_art = BLANK_IMAGE_URL
        embed.set_thumbnail(url=film_art)

        await ctx.send(embed=embed)

    async def get_game(self, ctx, game_link):
        r, status = await self.get_html(game_link)
        if status != 200:
            if status == 404:
                return await ctx.send('Game does not exist.')
            return await ctx.send('Could not connect to Glitchwave. (Sent by {})'.format(ctx.message.author.mention))
        game = BeautifulSoup(r, 'lxml')

        if game.text == '404: File not found':
            return await ctx.send('No game found.')

        game_title = game.find('h1', class_='page_object_header_title').text.replace('\n', '')

        try:
            description = 'Released: {}\n'.format(game.find('div', class_='page_object_header_left').text.replace('\n', ''))
        except:
            description = 'Released: \n'
        try:
            description += '{}\n'.format(game.find('div', class_='page_object_header_right').text.strip())
        except:
            description += 'Developer / Publisher: \n'
        try:
            description += 'Glitchwave Rating: {} / 5.00 from {} ratings\n'.format(game.find('span', class_='rating_number').text, game.find_all('div', class_='rating_card_description')[1].contents[0].strip())
        except:
            description += 'Glitchwave Rating: \n'
        try:
            description += 'Ranked: {}\n\n'.format(game.find_all('div', class_='rating_card_description')[2].text)
        except:
            description += '\n'
        try:
            description += 'Genres: '
            genres = game.find('div', class_='main_info_field_genres').find_all('a', class_='genres')
            for genre in genres[:-1]:
                description += '{}, '.format(genre.text)
            description += '{}\n'.format(genres[-1].text)
        except:
            description += '\n'
        try:
            description += 'Influences: '
            sec_genres = game.find('div', class_='main_info_field_sec_genres').find_all('a', class_='sec_genres')
            for sec_genre in sec_genres[:-1]:
                description += '{}, '.format(sec_genre.text)
            description += '{}\n'.format(sec_genres[-1].text)
        except:
            description += '\n'
        description += '\n{} (Sent by {})'.format(game_link, ctx.author.mention)
        
        title = '**{}**'.format(game_title)
        colour = ctx.author.colour

        embed = discord.Embed(title=title, description=description, colour=colour)

        try:
            game_art = 'https:' + game.find('div', class_='page_object_image').find('img')['src']
        except:
            game_art = BLANK_IMAGE_URL
        embed.set_thumbnail(url=game_art)

        await ctx.send(embed=embed)

    @commands.group(pass_context=True, invoke_without_command=True)
    async def rym(self, ctx, q=None):
        if q is None:
            q = q if q else await self.get_rym_username(ctx)
            if not q:
                return await ctx.send('Rateyourmusic username not set. Try .rym set [username].')
        elif 'rateyourmusic.com/release/' in q:
            return await self.get_release(ctx, q)
        elif 'rateyourmusic.com/film/' in q:
            return await self.get_film(ctx, q)
        return await self.get_rym_user(ctx, q)

    @rym.command(pass_context=True)
    async def set(self, ctx, username=None):
        if not username:
            return await ctx.send('No username provided.')
        conn = await self.bot.pool.acquire()
        async with conn.transaction():
            q = '''
                INSERT INTO rym_usernames (discord_id, username)
                  VALUES ($1, $2)
                ON CONFLICT (discord_id)
                DO
                  UPDATE
                    SET rym_username = $2;'''
            await self.bot.pool.execute(q, ctx.author.id, username)
        await self.bot.pool.release(conn)
        await ctx.send('Rateyourmusic username set to {}.'.format(username))

    @commands.group(pass_context=True, invoke_without_command=True)
    async def glitchwave(self, ctx, q=None):
        if q is None:
            return await ctx.send('Rateyourmusic username not set. Try .rym set [username].')
        elif 'glitchwave.com/game/' in q:
            try:
                await ctx.message.delete()
            except:
                await ctx.send('Tried to delete last message. Try reassigning roles to bot.')
            return await self.get_game(ctx, q)
        return await ctx.send('Something went wrong.')

def setup(bot):
    bot.add_cog(RateYourMusic(bot))
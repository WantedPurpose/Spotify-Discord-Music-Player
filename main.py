import os
import discord
from discord.ext import commands
import spotipy
import asyncio
from spotipy.oauth2 import SpotifyClientCredentials


intents = discord.Intents().all()
client = commands.Bot(command_prefix = '=',  intents=intents)

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id='YOUR_CLIENT_ID', client_secret='YOUR_CLIENT_SECRET'))


async def play_song(ctx, song_uri):
    # Get the track preview URL and create a Discord voice client
    track_info = sp.track(song_uri)
    preview_url = track_info['preview_url']
    voice_client = await ctx.author.voice.channel.connect()

    # Play the song and disconnect when finished
    voice_client.play(discord.FFmpegPCMAudio(preview_url))
    await ctx.send(f"Now playing: {track_info['name']}")
    while voice_client.is_playing():
        await asyncio.sleep(1)
    await voice_client.disconnect()


async def search_and_select(ctx, query):
    # Search for the song on Spotify
    results = sp.search(q=query, type='track')
    if len(results['tracks']['items']) == 0:
        await ctx.send("Sorry, I couldn't find that song on Spotify.")
        return

    # Display a list of search results to the user
    tracks = results['tracks']['items']
    tracks_str = ""
    for i, track in enumerate(tracks):
        tracks_str += f"{i+1}. {track['name']} - {track['artists'][0]['name']}\n"
    await ctx.send(tracks_str)

    # Wait for the user to select a song
    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel

    try:
        msg = await client.wait_for('message', check=check, timeout=30.0)
    except asyncio.TimeoutError:
        await ctx.send("Sorry, you took too long to respond.")
        return
    try:
        index = int(msg.content) - 1
        if index < 0 or index >= len(tracks):
            raise ValueError
    except ValueError:
        await ctx.send("Sorry, that's not a valid number.")
        return

    # Play the selected song
    await play_song(ctx, tracks[index]['uri'])


# Search for a song command
@client.command()
async def search(ctx, *, query):
    if not ctx.author.voice:
        await ctx.send("You need to be in a voice channel to use this command.")
        return
    await search_and_select(ctx, query)


# Play a song command
@client.command()
async def play(ctx, *, song_name):
    if not ctx.author.voice:
        await ctx.send("You need to be in a voice channel to use this command.")
        return
    # Search for the song on Spotify
    results = sp.search(q=song_name, type='track')
    if len(results['tracks']['items']) == 0:
        await ctx.send("Sorry, I couldn't find that song on Spotify.")
        return

    # Get the first track from the search results
    track_uri = results['tracks']['items'][0]['uri']
    await play_song(ctx, track_uri)

@client.command()
async def dc(ctx):
    voice_client = ctx.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
        await ctx.send("Successfully disconnected from the voice channel.")
    else:
        await ctx.send("I am not connected to a voice channel.")



@client.event
async def on_ready():
    print(f'Log : {client.user}')






client.run("TOKEN")

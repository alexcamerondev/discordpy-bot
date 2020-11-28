from classes.logs import Logs
from classes.whitelist import WhiteList
from classes.musicplayer import MusicPlayer
from classes.private.api import API
from classes.autoposter import AutoPoster
import classes.settings
import discord
from discord.ext.commands import Bot
import os
import json
import atexit
from colorama import deinit, Fore
import asyncio
import ctypes
import ctypes.util
from datetime import date
from classes.channel import Channel

COMMAND_PREFIX = '!'

#Environment 
BOT_TOKEN = os.getenv("BOT_TOKEN")
DISCORD_OWNER = os.getenv("DISCORD_OWNER")
logger = Logs('server')
whitelist = WhiteList()
bot = Bot(command_prefix=COMMAND_PREFIX,case_insensitive=True)
server_connected = False
#https://discordpy.readthedocs.io/en/latest/migrating.html
#https://discordpy.readthedocs.io/en/latest/faq.html#how-do-i-send-a-message-to-a-specific-channel
#Bot Events
@bot.event
async def on_ready():

    ctypes.windll.kernel32.SetConsoleTitleW("Discord Bot")
    logger.log("Discord bot up and running..", Fore.LIGHTGREEN_EX)
    await initial_activity(name="Starting up engines") 
    logger.log(f"Loaded whitelists", Fore.GREEN)
    global music_player
    music_player = MusicPlayer(bot,"Music")
    global api 
    api = API(whitelist)
    global autoposter
    autoposter = AutoPoster('news', bot, api)
    
    global server_connected
    server_connected = True
    # await keep_alive()
    
@bot.event
async def on_message(message):
    try:
        if message.author == bot.user:
            return
        if str(message.author) in whitelist.publicwhitelist['discord_users'] or str(message.author) in whitelist.adminwhitelist['discord_users']:
            await bot.process_commands(message)
    except Exception as e:             
        logger.log(f"Exception occurred :: {repr(e)}", Fore.RED)   

@bot.event
async def on_disconnect():
    logger.log("Client disconnected.")

@bot.event
async def on_message_delete(message):
    if message.author == bot.user:
        return
    logger.log(f"Message deleted: {message.content} by {message.author}", Fore.RED)
    
@bot.event
async def on_message_edit(before, after):
    if before.author == bot.user:
        return
    logger.log(f"User {before.author} edited message {before.content} to {after.content}", Fore.YELLOW)           
#End Bot Events

def exit_methods():
    #Attempt to ensure we are closing any loops that the bot is executing within modules, first we stop, then close.
    try:
        loop_running = bot.loop.is_running()
        logger.log(f"Event loop running: {loop_running}")  
        if loop_running:
            bot.loop.stop()
        else:
            if bot.loop.is_closed() is not True:
                bot.loop.close()
    except Exception as e:         
        logger.log(f"Exception occurred :: {repr(e)}", Fore.RED)  
        
#Functions    
@atexit.register
def exit_handler():
    exit_methods()
    deinit()
    logger.log("Bot terminated.", Fore.RED)      

async def initial_activity(name="Starting up engines", activity=discord.ActivityType.playing):   
    await bot.change_presence(activity=discord.Activity(name=name, type=activity))

async def get_user(username):
    member = discord.utils.find(lambda m: m.name == username, bot.get_all_members()) # This is only way I could find, it suggests getting all members then filtering as opposed to direct filter prior?
    return member

async def get_user_obj(user_id):
    user = bot.get_user(user_id) # This is only way I could find, it suggests getting all members then filtering as opposed to direct filter prior?
    return user

def start_bot():
    try:  
        bot.loop.run_until_complete(bot.start(BOT_TOKEN))  
    except KeyboardInterrupt:  
        exit_methods()
        bot.loop.run_until_complete(bot.logout())  
    # finally:  
    #     bot.loop.close()  

@bot.command()
async def auto_post(ctx):
    if str(ctx.message.author) in whitelist.adminwhitelist['discord_users'] or str(ctx.message.author) in whitelist.publicwhitelist['discord_users']:
        try:      
            if autoposter.is_running is not True:
                autoposter.is_running = True
                logger.log(f"Autoposter requested by {ctx.message.author}")
                await autoposter.start_news_queue()      
            else:
                await ctx.message.channel.send('Autoposter already running.')
            # await autoposter.daily_weather_poster(10)
        except Exception as e:             
            logger.log(f"Exception occurred :: {repr(e)}", Fore.RED)    
        return None

#Public BOT Commands
#https://discordpy.readthedocs.io/en/async/api.html#discord.opus.load_opus voice and youtube music
# Step 1: pip or pipenv install pynacl and install -U discord.py[voice]
# Step 2: Find libopus dll on the depths of the internet and manually load it
@bot.command()
async def next(ctx):
    if str(ctx.message.author) in whitelist.adminwhitelist['discord_users'] or str(ctx.message.author) in whitelist.publicwhitelist['discord_users']:
        music_player.next_song()
        
@bot.command()
async def pause(ctx):
    if str(ctx.message.author) in whitelist.adminwhitelist['discord_users'] or str(ctx.message.author) in whitelist.publicwhitelist['discord_users']:
        await music_player.pause_voice()
        
@bot.command()
async def resume(ctx):
    if str(ctx.message.author) in whitelist.adminwhitelist['discord_users'] or str(ctx.message.author) in whitelist.publicwhitelist['discord_users']:
        await music_player.resume_voice()
        
@bot.command()
async def stop(ctx):
    if str(ctx.message.author) in whitelist.adminwhitelist['discord_users'] or str(ctx.message.author) in whitelist.publicwhitelist['discord_users']:
        await music_player.stop_voice()
        
@bot.command()
async def leave(ctx):
    if str(ctx.message.author) in whitelist.adminwhitelist['discord_users'] or str(ctx.message.author) in whitelist.publicwhitelist['discord_users']:
        await music_player.voice_client.disconnect()
        
@bot.command()
async def music(ctx):
    try:
        if str(ctx.message.author) in whitelist.adminwhitelist['discord_users'] or str(ctx.message.author) in whitelist.publicwhitelist['discord_users']:       
            logger.log(f"isPlaying: {music_player.is_playing}")
            if music_player.is_playing is not True:
                music_player.is_playing = True
                logger.log(f"Music bot requested by {ctx.message.author}")
                await music_player.play_music_dir()         
            else:
                await ctx.message.channel.send('Music is already playing, you must !leave to reset it or !next to go to next in queue, and !resume to unpause a !pause.')
    except Exception as e:             
        logger.log(f"Exception occurred :: {repr(e)}", Fore.RED)    

@bot.command()
async def cat(ctx):
    if(str(ctx.message.author) in whitelist.publicwhitelist['discord_users'] or str(ctx.message.author) in whitelist.adminwhitelist['discord_users']):
        await ctx.message.channel.send(await api.cat_pictures())
        
@bot.command()
async def msg(ctx, user):
    user = user.mention
    logger.log(f"user mention:S? {user}")
    if(str(ctx.message.author) in whitelist.publicwhitelist['discord_users'] or str(ctx.message.author) in whitelist.adminwhitelist['discord_users']):
        user = await get_user(user)
        logger.log(f"User object {user}")
        await user.send('REEEEEEEEEEEEEEEEEEEEETEST')
        
@bot.command()
async def msgs(ctx, channel='legendary'):
    if(str(ctx.message.author) in whitelist.publicwhitelist['discord_users'] or str(ctx.message.author) in whitelist.adminwhitelist['discord_users']):
        channel_message_list = await Channel(channel, bot).flatten_channel_messages_tolist(400)
        for message in channel_message_list:
            message.content = message.content.strip()
            if(message.author != bot.user):               
                if(not message.content.startswith(COMMAND_PREFIX) and message.content != "" or None and not message.is_system()): #Filter commands and empty strings
                    logger.log(f"{message.created_at.strftime('%A, %B %d %Y @ %I:%M:%S %p')} -> {message.author} -> {message.content}")
                if(message.is_system()):
                     logger.log(f"System message: {message.system_content} @ {message.created_at.strftime('%A, %B %d %Y @ %I:%M:%S %p')}", Fore.MAGENTA)
        logger.log(f"Total Messages: {len(channel_message_list)}")
#END Public BOT Commands

# Admin Commands
@bot.command()
async def hweather(ctx):
    """
    Need to automate this task in order to be able get the full forecast.
    """
    if(str(ctx.message.author) in whitelist.publicwhitelist['discord_users'] or str(ctx.message.author) in whitelist.adminwhitelist['discord_users']):
        await ctx.message.channel.send(await api.hourly_weather())

@bot.command()
async def weather(ctx):
    if(str(ctx.message.author) in whitelist.publicwhitelist['discord_users'] or str(ctx.message.author) in whitelist.adminwhitelist['discord_users']):
        await ctx.message.channel.send(await api.daily_weather())
    
#Gets news by default from beginnging of this year to 2017 but u can alter that the default is for optimizing requests to the API as we only get 500 per day
@bot.command()
async def news(ctx, news_topic, from_date=date.today(), to_past_date="2019"):
    if(str(ctx.message.author) in whitelist.publicwhitelist['discord_users'] or str(ctx.message.author) in whitelist.adminwhitelist['discord_users']):
        await ctx.message.channel.send(await api.news(news_topic, from_date, to_past_date))
        
@bot.command() #await ban(user, *, reason=None, delete_message_days=1)
async def kill(ctx):
    try:
        if(str(ctx.message.author) in whitelist.adminwhitelist['discord_users']):   
            exit_methods()
            await bot.logout()
    except Exception as e:             
        logger.log(f"Exception occurred :: {repr(e)}", Fore.RED)  
         
@bot.command() #await ban(user, *, reason=None, delete_message_days=1)
async def ban(ctx, username, reason=None, delete_message_days=1):
    try:
        if(str(ctx.message.author) in whitelist.adminwhitelist['discord_users']):   
            member = await get_user(username)   
            if(member != None): 
                await member.ban(reason=reason, delete_message_days=delete_message_days)
    except Exception as e:             
        logger.log(f"Exception occurred :: {repr(e)}", Fore.RED)  
         
@bot.command() 
async def kick(ctx, username, reason=None):
    try:
        if(str(ctx.message.author) in whitelist.adminwhitelist['discord_users']):   
            member = await get_user(username)   
            if(member != None): 
                await member.kick(reason=reason)
                logger.log(f"Kicked {member} from group")
    except Exception as e:             
        logger.log(f"Exception occurred :: {repr(e)}", Fore.RED)   
               
@bot.command()
async def wl(ctx, username):
    if(str(ctx.message.author) in whitelist.adminwhitelist['discord_users']):
        try:
            whitelist.publicwhitelist['discord_users'].append(username)           
            whitelist.savewhitelists()
            logger.log(f"User {ctx.message.author} added {username} to public white list -> {whitelist.publicwhitelist['discord_users']}", Fore.GREEN)
        except Exception as e:             
            logger.log(f"Exception occurred :: {repr(e)}", Fore.RED)           
           
@bot.command()
async def echo(ctx, message: str):
    if(str(ctx.message.author) in whitelist.adminwhitelist['discord_users']):
        await ctx.send(message)
    
@bot.command()
async def clear(ctx, number = 14):
    if(str(ctx.message.author)in whitelist.adminwhitelist['discord_users']):
        try:
            msgs = []
            number = int(number)
            async for x in ctx.message.channel.history(limit=number+1):#add one to number to auto remove our command
                msgs.append(x)
            await ctx.message.channel.delete_messages(msgs)
            logger.log(f"User {ctx.message.author} finished deleting messages in channel {ctx.message.channel} with count of {number}", Fore.GREEN)
        except Exception as e:
            logger.log(f"Exception occurred :: {repr(e)}", Fore.RED)

@bot.command()
async def botact(ctx, name="Starting up engines", activity="playing"):
    """Name: Name of your status and Activity: streaming, playing, listening, watching are accepted parameters"""
    if(str(ctx.message.author) in whitelist.adminwhitelist['discord_users']):
        try:     
            activity = str.lower(activity)
            activityMock = discord.ActivityType.playing
            if "playing" in activity:
                activityMock = discord.ActivityType.playing
            if "listening" in activity:
                activityMock = discord.ActivityType.listening
            if "watching" in activity:
                activityMock = discord.ActivityType.watching
            if "streaming" in activity:
                activityMock = discord.ActivityType.streaming        
            final_activity = discord.Activity(name=name, type=activityMock)
            await bot.change_presence(activity=final_activity)
        except Exception as e:             
            logger.log(f"Exception occurred :: {repr(e)}", Fore.RED)   

start_bot()
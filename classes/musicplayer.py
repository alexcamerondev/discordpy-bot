
import discord
from classes.logs import Logs
from colorama import Fore
import os
from mutagen.mp3 import MP3
import asyncio
from classes.channel import Channel

class MusicPlayer:
    #For now you must hard core your pathways to your dll/executables for voice. 
    FFMPEG_URL_PATH = "D:\\Projects\\Python\\discordbotpulledfromcloud\\DiscordBot\\ffmpeg\\ffmpeg.exe"
    OPUS_FILE_PATH = "D:\\Projects\\Python\\discordbotpulledfromcloud\\DiscordBot\\opus\\libopus-0.x86.dll"
    """Have your discord bot join a voice channel and play music from a local file directory or youtube (coming soon)"""
    def __init__(self, bot, channel_name="Music"):
        self.logger = Logs('musicplayer')
        try:
            discord.opus.load_opus(self.OPUS_FILE_PATH)
            self.logger.log(F"Discord opus enabled: {discord.opus.is_loaded()}")
        except Exception as e:
            self.logger.log(f"Exception occurred :: {repr(e)}", Fore.RED) 
        self.channel_name = channel_name
        self.bot = bot
        self.channel_utility = Channel(channel_name, bot)
        self.voice_channel_id = self.channel_utility.channel_id   
        self.voice_channel = self.channel_utility.channel
        self.voice_client = None
        self.songs = asyncio.Queue()
        self.play_next_song = asyncio.Event()
        self.is_playing = False
        self.is_paused = False
        self.auto_play = True 
        self.current_song = None
        self.audio_player_running = True
        self.song_skip = False
        self.songs_source = {}
        self.previous_source_queue = None #Used for storing the last played song so we could reinstaniate it if needed. 
        self.logger.log(f"Music player constructed.")
        
    async def aud_player(self):
        try:    
            while self.audio_player_running:
                self.play_next_song.clear()
                self.songs_source = await self.songs.get()#Get our songs
                await self.change_status(self.songs_source['name'])#Update bot status to song name
                self.current_song = self.songs_source['name']#Set our current song
                self.current_song_path = self.songs_source["path"] 
                source = await discord.FFmpegOpusAudio.from_probe(self.current_song_path, executable=self.FFMPEG_URL_PATH, method='fallback')#Create local FFMPEG process to play mp3
                self.voice_client.play(source, after=self.on_after)#Invoke discord client to play our ffmpeg source with onafter function hook.
                self.logger.log(f"Playing {self.songs_source['name']} with a duration of {self.songs_source['length']}s")
                await self.play_next_song.wait() #This will block the thread until we finish our task aka mp3 song in this case.       
        except Exception as e:
            self.play_next_song.clear()#Clear our internal flags
            self.songs_source = {}  #Reset the entire dictionary object as something bad happened and we want out.
            self.audio_player_running = False #Force loop to exit.
            self.is_playing = False #Quit playing
            self.logger.log(f"Exception aud_player :: {repr(e)}", Fore.RED)   
            
    async def change_status(self, name="Bumpin tunes", activity="playing"):
        """Name: Name of your status and Activity: streaming, playing, listening, watching are accepted parameters"""
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
            await self.bot.change_presence(activity=final_activity)
        except Exception as e:             
            self.logger.log(f"Exception change_status :: {repr(e)}", Fore.RED)   
            
    async def get_music_urls_from_dir(self,dir_path, file_ext = "mp3"):
        music_track_number = 0
        song_dict = {}
        try:      
            with os.scandir(dir_path) as it:
                for entry in it:
                    if not entry.name.startswith('.') and entry.is_file() and entry.name.endswith(f".{file_ext}"):
                        music_track_number = music_track_number + 1
                        path = str(entry.path)
                        audio = MP3(path) #pip install mutagen for getting mp3 data such as duration
                        song_dict[music_track_number] = {
                            "name" : entry.name,
                            "length" : audio.info.length, 
                            "path" : path
                        }                      
            return song_dict   
        except Exception as e:             
            self.logger.log(f"Exception get_music_urls_from_dir :: {repr(e)}", Fore.RED)    
        return None           
    
    async def play_music_dir(self, music_directory = r"D:\Music", file_type = "mp3"):     
        """Name: Gathers a list of all music file types and plays them in sequence collected."""
        try:
            self.voice_client = await self.voice_channel.connect()
            music_dict = await self.get_music_urls_from_dir(music_directory, file_type)     
            if music_dict is not None:
                for id, song_data in music_dict.items():#This should allow us to run timer code so it will play the next song as one finishes.
                    self.logger.log(f"Added {id} - {song_data['name']}")  #returned url paths.
                    await self.songs.put(song_data)        
                self.logger.log(f"Finished added all songs in directory to queue system", Fore.GREEN)
                self.bot.loop.create_task(self.aud_player())
        except Exception as e:
            self.is_playing = False
            await self.voice_client.disconnect()
            self.logger.log(f"Exception play_music_dir :: {repr(e)}", Fore.RED)    
            
    def next_song(self):
        """Will switch to next song in current queue."""
        try:
            self.song_skip = True
            self.voice_client.pause()
            self.voice_client.stop()
            self.bot.loop.call_soon_threadsafe(self.play_next_song.set)  
        except Exception as e:
            self.logger.log(f"Exception next_song :: {repr(e)}", Fore.RED)    
        
    async def pause_voice(self):
        """Will pause the current song playing."""
        self.voice_client.pause()
        self.is_paused = True  
        await self.change_status(f"(paused) - {self.current_song}")
         
    async def resume_voice(self):
        """Will resume the current song playing."""
        self.voice_client.resume()
        self.is_paused = False  
        await self.change_status(self.current_song)
    
    async def stop_voice(self):
        """Will stop the song from playing and left channel"""
        self.voice_client.stop()
        await self.leave_voice()
        self.is_paused = False
        self.is_playing = False
            
    async def leave_voice(self):
        """Will stop the song from playing and left channel"""
        await self.change_status('Chillin')
        self.voice_client.stop()
        await self.voice_client.disconnect()
        self.is_paused = False
        self.is_playing = False
            
    def on_after(self,e):     
        if(e):
            self.logger.log(f"error: {e}", Fore.RED)
        else:
            if(self.auto_play):
                try:
                    if(self.song_skip):
                        self.song_skip = False
                    else: #if not skipping song then auto play next song
                        self.bot.loop.call_soon_threadsafe(self.play_next_song.set)   
                except Exception as e:
                     self.logger.log(f"Exception occurred on_after :: {repr(e)}", Fore.RED)    
            

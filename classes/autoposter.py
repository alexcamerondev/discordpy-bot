import discord
from classes.logs import Logs
from colorama import Fore
import os
from mutagen.mp3 import MP3
import asyncio
from classes.channel import Channel
import time, sched
# from threading import Timer
import threading
import random

class AutoPoster:
    HALF_HOUR = 1800
    HOUR = 3600
    __NEWS_INTERVAL = 30
    
    def __init__(self, channel_name, bot, api):
        #Dependency injections
        self.logger = Logs('autoposter')
        self.bot = bot
        self.channel_utility = Channel(channel_name, bot) #Gets us the channel to post in
        self.text_channel = self.channel_utility.channel
        self.api = api #bring in our api data

        #Main queue running flag
        self.auto_poster_queue_running_flag = True
        self.is_running = False
        self.queue_playing = False
        
        #News Queue stuff
        self.news_queue = asyncio.Queue()#Setup a queue
        self.news_next_in_queue = asyncio.Event()
        self.current_news = None
        self.news_topics = ['trump', 'trudeau', 'canada', 'aquaculture', 'environment', 'tesla', 'spacex', 'lobster','programming', 'reactjs', 'runescape','osrs', 'world of warcraft' ] #Can improve this to be a dictionary later and populate from file.
        self.news_timer = None
        
        #Weather Queue Stuff
        self.weather_queue = asyncio.Queue()
        self.weather_next_in_queue = asyncio.Event()
        self.current_weather = None
        
    async def random_news_topic(self):
        return str(random.choice(self.news_topics))  
     
    async def auto_poster_loop(self):
        try:    
            while self.auto_poster_queue_running_flag:
                self.news_next_in_queue.clear()
                self.current_news = await self.news_queue.get()
                await self.channel_utility.send_to("meme",await self.api.cat_pictures()) #Send cat pictures to the meme channel
                await self.channel_utility.send(await self.api.news(self.current_news['topic']))
                await asyncio.sleep(self.HALF_HOUR)
                self.bot.loop.call_soon_threadsafe(self.news_next_in_queue.set)  
                await self.news_next_in_queue.wait() 
            
            #Reset vars here when the while loop exits:
            
        except Exception as e:
            self.news_next_in_queue.clear()          
            self.auto_poster_queue_running_flag = False
            self.is_running = False
            self.logger.log(f"Exception auto_poster_loop :: {repr(e)}", Fore.RED)
            
        
    #A function even ron burgundy has no access to.
    async def __create_news(self):
        index = 0
        news_dictionary = {}
        for topic in self.news_topics:
            #We will generate posts to queue for a timelimit. Using dictionary to serialize and save as json\
            #Will have to build the topics into database to easily update them.
            news_dictionary[index] = {
                "topic": topic
            }
            index = index + 1
        return news_dictionary
    
    async def start_auto_posting(self):
        self.bot.loop.create_task(self.auto_poster_loop())
    
    async def start_news_queue(self):
        news_dict = await self.__create_news()
        for id, news_data in news_dict.items():
            await self.news_queue.put(news_data)
        await self.start_auto_posting()

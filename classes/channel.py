from classes.logs import Logs
import discord

class Channel:
    def __init__(self, channel_name, bot):
        self.bot = bot
        self.logger = Logs('channel')
        self.channel_name = channel_name
        self.channel = self.get_channel_object()
        self.channel_id = self.get_channel_id_by_name()
        
    def get_channel_id_by_name(self):
        channel_id = discord.utils.get(self.bot.get_all_channels(), name=self.channel_name).id
        # self.logger.log(f"Channel id: {channel_id}")
        return channel_id

    def get_channel_object(self):
        channel = discord.utils.get(self.bot.get_all_channels(), name=self.channel_name)
        # self.logger.log(f"Channel object: {channel}")
        return channel
    
    async def flatten_channel_messages_tolist(self, limit=123):
        messages = await self.channel.history(limit=limit).flatten()
        return messages
    
    async def send(self, msg):
        await self.channel.send(msg)
        
    async def send_to(self, channel_name, msg):
        """Send message to a specific channel given a channel name parameter"""
        await Channel(channel_name, self.bot).channel.send(msg) #Spawn instance of a new channel
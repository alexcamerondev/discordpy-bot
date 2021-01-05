from datetime import datetime,date
from classes.logs import Logs
from pathlib import Path
import json
from colorama import Fore
logger = Logs('whitelist')
class WhiteList:
    """For creating white lists for command access and saving to disk"""
    def __init__(self):
        self.publicwhitelist = {}
        self.adminwhitelist = {}
        self.publicwhitelist['discord_users'] = []
        self.adminwhitelist['discord_users'] = []
        
        self.initial_creation() # create if don't exist
        
        #load the admin file
        self.publicwhitelist = self.load_public_whitelist()
        self.adminwhitelist = self.load_admin_whitelists()
        #create our file structure for the whitelist

    def initial_creation(self):
        try:            
            # Need to check if the file has any data.         
            Path("whitelist").mkdir(parents=True, exist_ok=True)
            adminpath = Path("whitelist/adminwhitelist.txt")
            if adminpath.is_file() == False:
                logger.log('Creating admin white list file')
                with open('whitelist/adminwhitelist.txt', 'w') as savefile:
                    json.dump(self.adminwhitelist, savefile)

            publicpath = Path("whitelist/publicwhitelist.txt")
            if publicpath.is_file() == False:
                logger.log('Creating public white list file')
                with open('whitelist/publicwhitelist.txt', 'w') as savefile:
                    json.dump(self.publicwhitelist, savefile)
        except Exception as e:             
            logger.log(f"Exception occurred :: {repr(e)}")  
              
    def savewhitelists(self):
        try:            
            # Need to check if the file has any data. 
            logger.log('Saving admin and public whitelist')
            Path("whitelist").mkdir(parents=True, exist_ok=True)
            with open('whitelist/adminwhitelist.txt', 'w') as savefile:
                json.dump(self.adminwhitelist, savefile)
            with open('whitelist/publicwhitelist.txt', 'w') as savefile:
                json.dump(self.publicwhitelist, savefile)
        except Exception as e:             
            logger.log(f"Exception occurred :: {repr(e)}")     
                
    def load_admin_whitelists(self):
        try:
            logger.log('Loading admin whitelist')
            with open('whitelist/adminwhitelist.txt') as json_file:
                data = json.load(json_file)
                return data
        except Exception as e:             
            logger.log(f"Exception occurred :: {repr(e)}")  
        return {}
            
    def load_public_whitelist(self):
        try:
            logger.log('Loading public whitelist')
            with open('whitelist/publicwhitelist.txt') as json_file:
                data = json.load(json_file)
                return data
        except Exception as e:             
            logger.log(f"Exception occurred :: {repr(e)}", Fore.RED)  
        return {}
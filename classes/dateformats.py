
from datetime import datetime, date
from classes.logs import Logs
from colorama import Fore
class DateFormats:

    def __init__(self, date_string):
        self.logger = Logs('dateformats')
        self.date_string = date_string
        
    async def convert_utc_time(self):     
        try:      
            #Store in our DateTime object
            weather_date = datetime.strptime(self.date_string, "%Y-%m-%dT%H:%M:%S%z")#2020-04-08T06:54:00-03:00   
            #Timestamp    
            datestamp = weather_date.strftime("%d-%b-%Y (%I:%M:%S %p)") #Convert to human readable 
            return datestamp   
        except Exception as e:             
            self.logger.log(f"Exception occurred :: {repr(e)}", Fore.RED)    
        return None

    async def format_weather_date(self):     
        try:      
            #Store in our DateTime object
            weather_date = datetime.strptime(self.date_string, "%Y-%m-%dT%H:%M:%S%z")#2020-04-08T06:54:00-03:00   
            #Timestamp    
            time_stamp = weather_date.strftime("%I:%M:%S %p") #Convert to human readable 
            return time_stamp   
        except Exception as e:             
            self.logger.log(f"Exception occurred :: {repr(e)}", Fore.RED)    
        return None

    async def hourly_weather_format(self):     
        try:      
            #Store in our DateTime object
            weather_date = datetime.strptime(self.date_string, "%Y-%m-%dT%H:%M:%S%z")#2020-04-08T06:54:00-03:00   
            #Timestamp    
            hourly_time = weather_date.strftime("%I:%M:%S %p") #Convert to human readable 
            return hourly_time
        except Exception as e:             
            self.logger.log(f"Exception occurred :: {repr(e)}", Fore.RED)    
        return None


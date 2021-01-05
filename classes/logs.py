from datetime import datetime,date
from pathlib import Path
import inspect 
from colorama import init, Fore, Back, Style
class Logs:
    """For logging throughout application code"""
    def __init__(self, module_name, error_only = False):
        init()
        self.module_name = module_name     
        self.error_only = error_only   
        
    def log(self, log="", color=Fore.CYAN):     
        """Logs our application data in a smart way. \n\nTodo: add module chain bubble to show stacktrace of all paths to the function call point"""   
        if(self.error_only == True):          
            if "Exception" in log or "Error" in log:
                self.print_template(color + log + Style.RESET_ALL)
        else:   
            self.print_template(color + ' ' + log + ' ' + Style.RESET_ALL)
                      
    def print_template(self, log):
        timestamp = datetime.now().strftime("%d-%b-%Y (%I:%M:%S %p)")
        log = f"{timestamp} :: {self.module_name} :: {inspect.stack()[2].function} :: {log}\n" # Two levels deep on functions to target where this is called upon
        print(log, end="")
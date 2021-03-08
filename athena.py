from configparser import ConfigParser
from datetime import datetime
import logging
from logging import Logger
import os
from time import ctime, sleep
import urllib.parse

from speech_service import SpeechService
from number_parser import parse

class AthenaCommand:
    full_text: str
    text: str
    done: bool = False

    def __init__(self, full_text: str):
        self.full_text = full_text
        self.text = full_text.lower().partition('athena')[2]
        
    def parse(self, phrase, handler):
        if not self.done and phrase.lower() in self.text:
            handler(self.text)
            self.done = True            
        return self
    
    def not_done(self, handler):
        if not self.done:
            handler(self.text)

MONTHS = [
    'January',
    'February',
    'March',
    'April',
    'May',
    'June',
    'July',
    'August',
    'September',
    'October',
    'November',
    'December',
]

DAYS = [
    'Sunday',
    'Monday',
    'Tuesday',
    'Wednesday',
    'Thursday',
    'Friday',
    'Saturday',
]

class Athena:
    speech_service: SpeechService
    log: Logger
    running: bool
        
    def __init__(self, speech_service: SpeechService, config: ConfigParser):
        self.speech_service = speech_service
        self.log = logging.getLogger(self.__module__)
        self.log.setLevel(config.get('Logging', 'level'))        


    def respond(self, response: str) -> None:
        """Respond to the user text provided

        Args:
            response (str): The text the response to the user.
        """
        self.speech_service.speak(response)
    
    def ready(self) -> str:
        """Set Athena ready to listen for commands

        Returns:
            str: The text of the command received
        """
        return self.speech_service.listen()
    
    
    def start(self) -> None:
        """Initializes Athena 
        """
        sleep(2)
        self.respond(
            f'Athena online, what can I do for you?')
        self.running = True
        while self.running:
            data = self.ready()
            if 'athena' in data.lower():
                try:
                    self.process(data)
                except Exception as e:
                    self.log.error(e)
            else:
                self.log.debug(f'Did not find "athena" in phrase "{data}"')

    def create_reminder(self, reminder: str):
        """Create a new reminder 

        Args:
            reminder str: The text of the request to set a reminder
        """
        reminder = reminder.partition('remind me to')[2]
        reminder = reminder.replace('my', 'your')
        self.respond(f'I\'m sorry, I\'m not able to set reminders yet but soon I will be able to remind you to "{reminder}"')
    
    def list_reminders(self):
        self.respond(f"I'm sorry, I'm not able to list your reminders yet.")
    
    def where_is(self, command: str):
        location = command.partition('where is')[2].strip()
        self.respond(f'One moment, I will show you where {location} is.')
        os.system(f'explorer https://www.google.com/maps/place/{urllib.parse.quote_plus(location)}/&amp;')
    
    def shutdown(self, command: str):
        self.respond(f'Okay, Athena, signing off.')
        self.running = False
    
    def process(self, command_text: str):
        command = AthenaCommand(command_text)
        command.parse(
            'remind me to', lambda x: self.create_reminder(x)
        ).parse(
            'what are my reminders' , lambda x: self.list_reminders(x)
        ).parse(
            'set a timer', lambda x: self.respond(f"Sorry, I am not able to set timers yet.")                
        ).parse(
            'how are you', lambda x: self.respond('I am well, thank you')
        ).parse(
            'what time is it', lambda x: self.respond(f'It is presently {ctime()}')    
        ).parse(
            'where is', lambda x: self.where_is(x)
        ).parse(
            'shut down', lambda x: self.shutdown(x)
        ).not_done(
            lambda x: self.respond(f'Sorry, I do not know what to do with the command "{x}"')
        )
    

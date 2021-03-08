from configparser import ConfigParser
import logging
from logging import Logger
import os
from uuid import uuid4
from threading import Thread

from gtts import gTTS
from playsound import playsound
import speech_recognition as sr
from speech_recognition import Recognizer, Microphone, UnknownValueError, RequestError, WaitTimeoutError

class CleanUpThread(Thread):
    working_directory: str
    log: Logger
    
    def __init__(self, config: ConfigParser):
        Thread.__init__(self)
        self.log = logging.getLogger(self.__module__)
        self.log.setLevel(config.get('Logging', 'level'))
    
    def run(self):
        try :
            for item in os.listdir(os.getcwd()):
                if item.endswith('.mp3'):
                    os.remove(os.path.join(os.getcwd(), item))
        except Exception as ex:
            self.log.error(f'Clean up failed: {ex}')

class SpeechService:
    log: Logger
    config: ConfigParser
    
    def __init__(self, config: ConfigParser):
        self.log = logging.getLogger(self.__module__)
        self.log.setLevel(config.get('Logging', 'level'))
        self.config = config

    def speak(self, audio_string):
        self.log.info(audio_string)
        tts = gTTS(text=audio_string, lang='en')
        file_path = os.path.join(os.getcwd(), f'{uuid4()}.mp3')
        tts.save(file_path)
        
        playsound(file_path)
        
        clean_up = CleanUpThread(self.config)
        clean_up.start()

    def listen(self) -> str:
        # Record Audio
        data = ''        
        recognizer = Recognizer()
        with Microphone() as source:
            self.log.debug('Listening on microphone...')
            try:
                audio = recognizer.listen(source, timeout=10)
            except WaitTimeoutError:
                self.log.debug('Listen timed out.')
                return data
        # Speech recognition using Google Speech Recognition
        try:
            # Uses the default API key
            # To use another API key: `r.recognize_google(audio, key='GOOGLE_SPEECH_RECOGNITION_API_KEY')`
            data = recognizer.recognize_google(audio)
            self.log.debug(f'You said: "{data}"')
        except UnknownValueError:
            self.log.debug('Google Speech Recognition could not understand audio')
        except RequestError as e:
            self.log.error(f'Could not request results from Google Speech Recognition service: {e}')

        return str(data)
from configparser import ConfigParser
import os
import logging
import logging.config

from athena import Athena
from rich.logging import RichHandler
from speech_service import SpeechService

logging.basicConfig(
    level=logging.CRITICAL,
    format='%(name)-15s %(message)s',
    datefmt='[%Y-%m-%d %H:%M:%S]',
    handlers=[RichHandler(rich_tracebacks=True)]
)
config = ConfigParser()
config.read_file(open('config.ini'))
cwd = os.getcwd()
# initialization

speech_service = SpeechService(config)
athena = Athena(speech_service, config)

try:
    athena.start()
except Exception as e:
    logging.error(e)
import os

from dotenv import load_dotenv

load_dotenv()

CHANNEL_NAME = os.getenv('CHANNEL_NAME')

BOT_NAMES = ['rexxauto', 'streamelements']
BOT_PREFIX = '!'

JOIN = 'JOIN'
PART = 'PART'
JUMP = 'JUMP'
COLOR = 'COLOR'

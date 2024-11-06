import os

from dotenv import load_dotenv

load_dotenv()

CHANNEL_NAME = os.getenv('CHANNEL_NAME')
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
DOMAIN = os.getenv('DOMAIN')
REDIRECT_URI = os.getenv('REDIRECT_URI')
STORE_URL = os.getenv('STORE_URL')
EXT_SECRET = os.getenv('EXT_SECRET')

BOT_NAMES = ['rexxauto', 'streamelements']
BOT_PREFIX = '!'

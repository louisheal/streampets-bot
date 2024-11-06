import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_NAME = os.getenv('CHANNEL_NAME')
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
DB_TOKEN = os.getenv('DB_TOKEN')
DB_URL = os.getenv('DB_URL')
DOMAIN = os.getenv('DOMAIN')
EXT_SECRET = os.getenv('EXT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')
OVERLAY_URL = os.getenv('OVERLAY_URL')
STORE_URL = os.getenv('STORE_URL')

BOT_NAMES = ['rexxauto', 'streamelements']
BOT_PREFIX = '!'

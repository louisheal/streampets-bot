import asyncio
import os
from pathlib import Path
import json

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from dotenv import load_dotenv

from queues import JsonQueue
from chat_bots import ChatBot
from message_announcer import MessageAnnouncer
from utils import CHANNEL_NAME
from models import Color
from database import LibSqlDatabase

load_dotenv()

########################
### Inititialisation ###
########################

BOT_TOKEN = os.getenv('BOT_TOKEN')
DB_TOKEN = os.getenv('DB_TOKEN')
DB_URL = os.getenv('DB_URL')
OVERLAY_URL = os.getenv('OVERLAY_URL')
STORE_URL = os.getenv('STORE_URL')

announcer = MessageAnnouncer()
queue = JsonQueue(Path('data','queue.json'))
database = LibSqlDatabase(DB_TOKEN, DB_URL)

#######################
### FastAPI Startup ###
#######################

bot = ChatBot(queue, database, announcer, os.getenv('BOT_TOKEN'), '!', [CHANNEL_NAME])

@asynccontextmanager
async def lifespan(app: FastAPI):
  asyncio.create_task(bot.connect())
  print("Bot running...")
  yield
  bot.close()

app = FastAPI(lifespan=lifespan)
app.add_middleware(
  CORSMiddleware,
  allow_origins=[OVERLAY_URL, STORE_URL],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

##############
### ROUTES ###
##############

@app.get('/listen')
async def listen():
  def stream():
    messages = announcer.listen()
    while True:
      msg = messages.get()
      yield msg

  return StreamingResponse(stream(), media_type='text/event-stream')

@app.get('/viewers')
async def viewers():
  rexs = bot.get_viewer_rexs()
  json_rexs = [rex.to_dict() for rex in rexs]
  return json_rexs

@app.get('/colors')
async def get_colors():
  colors = [color.name.lower() for color in Color]
  return colors

@app.put('/colors')
async def update_color(request: Request):
  data = request.json()
  color = Color.str_to_color(data['color'])
  trex = database.set_trex_color('ljrexcodes', color)
  announcer.announce(msg=json.dumps(trex.to_dict()), event='COLOR')
  return Response(status_code=status.HTTP_200_OK)

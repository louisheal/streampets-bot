from pathlib import Path

import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .json_queue import JsonQueue
from .announcer import MessageAnnouncer
from .database import Database
from .chat_bots import ChatBot
from .config import (
  BOT_PREFIX,
  BOT_TOKEN,
  CHANNEL_NAME,
  DB_TOKEN,
  DB_URL,
  OVERLAY_URL,
  STORE_URL,
)


announcer = MessageAnnouncer()
json_queue = JsonQueue(Path('data','queue.json'))
database = Database(DB_TOKEN, DB_URL)

bot = ChatBot(json_queue, database, announcer, BOT_TOKEN, BOT_PREFIX, [CHANNEL_NAME])

@asynccontextmanager
async def lifespan(app: FastAPI):
  bot.loop = asyncio.get_running_loop()
  await bot.connect()
  yield
  await bot.close()

def create_app():
  app = FastAPI(lifespan=lifespan)
  app.add_middleware(
    CORSMiddleware,
    allow_origins=[OVERLAY_URL, STORE_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
  )

  from .routes import router
  app.include_router(router)

  return app

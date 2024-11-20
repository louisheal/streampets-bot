import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .announcers import MultiChannelAnnouncer
from .bot import ChatBot
from .database import Database
from .config import (
  DB_TOKEN,
  DB_URL,
  OVERLAY_URL,
  STORE_URL,
)

announcer = MultiChannelAnnouncer()
database = Database(DB_TOKEN, DB_URL)
bot = ChatBot(database, announcer)

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

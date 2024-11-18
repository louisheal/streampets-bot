from twitchio.ext import commands

from app.announcer import MessageAnnouncer
from app.database import Database
from app.models import Viewer
from app.helix import get_user_id_by_username

from app.config import (
  CHANNEL_NAME,
  BOT_NAMES,
  BOT_PREFIX,
  BOT_TOKEN,
)


class ChatBot(commands.Bot):
  def __init__(self, db: Database, announcer: MessageAnnouncer):
    super().__init__(
      token=BOT_TOKEN,
      prefix=BOT_PREFIX,
      initial_channels=[CHANNEL_NAME],
    )
    self.announcer = announcer
    self.db = db
    self.user_ids = set()

    self.load_module("app.commands")

  def get_user_ids(self):
    return self.user_ids

  async def event_part(self, user):
    if user.name in BOT_NAMES:
      return
    
    user_id = get_user_id_by_username(user.name)
    if user_id in self.user_ids:
      self.announcer.announce_part(user_id)
      self.user_ids.remove(user_id)

  async def event_message(self, message):
    if not message.author or message.author.name in BOT_NAMES:
      return

    user_id = message.author.id
    if user_id not in self.user_ids:
      username = message.author.name
      color = self.db.get_current_color(user_id)

      self.user_ids.add(user_id)
      self.announcer.announce_join(Viewer(user_id, username, color))

    await self.handle_commands(message)
  
  @commands.command(name='commands')
  async def command_commands(self, ctx):
    commands = [f"!{command}" for command in self.commands.keys()]
    await ctx.send(' '.join(commands))

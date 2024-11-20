from twitchio.ext import commands

from app.announcers import MultiChannelAnnouncer
from app.database import Database
from app.models import Viewer, UserLRU

from app.config import (
  BOT_NAMES,
  BOT_PREFIX,
  BOT_TOKEN,
)


class ChatBot(commands.Bot):
  def __init__(self, db: Database, announcer: MultiChannelAnnouncer):
    super().__init__(
      token=BOT_TOKEN,
      prefix=BOT_PREFIX,
      initial_channels=[],
    )
    self.announcer = announcer
    self.db = db

    # ChannelName -> LruList
    self.lru: dict[str,UserLRU] = {}

    self.load_module("app.commands")

  def get_users(self, channel_name: str) -> list[Viewer]:
    if channel_name not in self.lru:
      self.lru[channel_name] = UserLRU()
    return self.lru[channel_name].get_viewers()

  async def event_message(self, message):
    if not message.author or message.author.name in BOT_NAMES:
      return
    
    channel_name = message.channel.name
    user_id = message.author.id
    username = message.author.name

    if channel_name not in self.lru:
      self.lru[channel_name] = UserLRU()

    if user_id not in self.lru[channel_name]:
      channel_id = self.db.get_channel_id(channel_name)
      color = self.db.get_current_color(user_id, channel_id)
      viewer = Viewer(user_id, username, color)

      removed_id = self.lru[channel_name].add(viewer)
      if removed_id:
        self.announcer.announce_part(channel_name, removed_id)

      self.announcer.announce_join(channel_name, viewer)
    else:
      self.lru[channel_name].update_user(user_id)

    await self.handle_commands(message)
    
  @commands.command(name='commands')
  async def command_commands(self, ctx: commands.Context):
    commands = [f"!{command}" for command in self.commands.keys()]
    await ctx.send(' '.join(commands))

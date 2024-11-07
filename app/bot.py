from twitchio.ext import commands

from app.announcer import MessageAnnouncer
from app.database import Database
from app.models import Color, Viewer

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
    self.user_ids: list[str] = []

  def get_user_ids(self):
    return self.user_ids

  async def event_part(self, user):
    if user.name in BOT_NAMES:
      return
    
    self.announcer.announce_part(user.id)
    if user.id in self.user_ids:
      self.user_ids.remove(user.id)

  async def event_message(self, message):
    if not message.author or message.author.name in BOT_NAMES:
      return

    user_id = message.author.id
    if user_id not in self.user_ids:
      username = message.author.name
      color = self.db.get_color_by_user_id(user_id)

      self.user_ids.append(user_id)
      self.announcer.announce_join(Viewer(user_id, username, color))

    await self.handle_commands(message)
  
  @commands.command(name='jump')
  async def command_jump(self, ctx):
    self.announcer.announce_jump(ctx.author.id)

  @commands.command(name='color')
  async def command_color(self, ctx, color):
    if color.lower() not in [c.name.lower() for c in Color]:
      await ctx.send(f"{color} is not an available color!")
      return
    
    user_id = ctx.author.id
    color = Color.str_to_color(color)

    self.db.set_color_by_user_id(user_id, color)
    self.announcer.announce_color(user_id, color)
  
  @commands.command(name='commands')
  async def command_commands(self, ctx):
    commands = [f"!{command}" for command in self.commands.keys()]
    await ctx.send(' '.join(commands))

  @commands.command(name='discord')
  async def command_discord(self, ctx):
    await ctx.send('https://discord.gg/kxcMEp8')

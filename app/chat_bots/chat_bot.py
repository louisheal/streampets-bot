from pathlib import Path
from twitchio.ext import commands

from .commands import setup_queue_commands, setup_tag_commands, setup_pet_commands
from app.json_queue import JsonQueue
from app.announcer import MessageAnnouncer
from app.database import Database

from app.config import CHANNEL_NAME, BOT_NAMES


class ChatBot(commands.Bot):

  def __init__(self, queue: JsonQueue, db: Database, announcer: MessageAnnouncer, token, prefix, channels):
    self.announcer = announcer
    super().__init__(
      token=token,
      prefix=prefix,
      initial_channels=channels,
    )
    self.queue = queue
    self.db = db
    self.curr_tag = CHANNEL_NAME.lower()
    self.failed_tags = []
    self.viewers = []
    self.tragic = 0

    self.load_module(Path('commands','pet_commands'))

    setup_queue_commands(self)
    setup_tag_commands(self)
    # setup_pet_commands(self)

  async def event_part(self, user):
    if user.name in BOT_NAMES:
      return
    
    self.announcer.announce_part(user.name)
    if user.name in self.viewers:
      self.viewers.remove(user.name)

  async def event_message(self, message):
    if not message.author or message.author.name in BOT_NAMES:
      return
    
    username = message.author.name

    if username not in self.viewers:
      trex = self.db.get_trex_by_username(username)
      # TODO: Announcer factory methods
      self.announcer.announce_join(username, trex.color)
      self.viewers.append(username)

    await self.handle_commands(message)

  def get_viewer_rexs(self):
    return self.db.get_all_trexs(self.viewers)
  
  @commands.command(name='tragic')
  async def command_tragic(self, ctx):
    self.tragic += 1
    await ctx.send(f"LJRex has said tragic {self.tragic} times!")

  @commands.command(name='commands')
  async def command_commands(self, ctx):
    commands = [f"!{command}" for command in self.commands.keys()]
    await ctx.send(' '.join(commands))

  @commands.command(name='rps')
  async def command_rps(self, ctx, choice: str):
    match choice.lower():
      case 'rock': await ctx.send('Paper! I win!')
      case 'paper': await ctx.send('Scissors! I win!')
      case 'scissors': await ctx.send('Rock! I win!')

  @commands.command(name='discord')
  async def command_discord(self, ctx):
    await ctx.send('https://discord.gg/kxcMEp8')

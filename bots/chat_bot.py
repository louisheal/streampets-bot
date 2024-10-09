from twitchio.ext import commands

from queues.simple_queue import SimpleQueue as IQueue
from .commands import setup_queue_commands, setup_tag_commands
from message_announcer import MessageAnnouncer
from database import Database

from utils import BOT_NAMES, CHANNEL_NAME


JOIN = 'JOIN'
PART = 'PART'
JUMP = 'JUMP'


class ChatBot(commands.Bot):

  def __init__(self, queue: IQueue, db: Database, token, prefix, channels, announcer: MessageAnnouncer):
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

    setup_queue_commands(self)
    setup_tag_commands(self)

  async def event_join(self, channel, user):
    if user.name not in BOT_NAMES:
      trex = self.db.get_rex_by_username(user.name)
      self.announcer.announce(msg=trex, event=JOIN)
      if user.name not in self.viewers:
        self.viewers.append(user.name)

  async def event_part(self, user):
    if user.name not in BOT_NAMES:
      trex = self.db.get_rex_by_username(user.name)
      self.announcer.announce(msg=trex, event=PART)
      if user.name in self.viewers:
        self.viewers.remove(user.name)

  async def event_message(self, ctx):
    if ctx.author and ctx.author.name not in self.viewers and ctx.author.name not in BOT_NAMES:
      self.announcer.announce(msg=ctx.author.name, event=JOIN)
      self.viewers.append(ctx.author.name)
    await self.handle_commands(ctx)

  def get_viewer_rexs(self):
    return self.db.get_all_rexs(self.viewers)

  @commands.command(name='jump')
  async def command_jump(self, ctx):
    self.announcer.announce(msg=ctx.author.name, event=JUMP)

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

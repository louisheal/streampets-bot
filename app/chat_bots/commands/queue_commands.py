from twitchio.ext import commands

from app.utils import to_ordinal
from app.config import CHANNEL_NAME


def setup_queue_commands(bot):

  @commands.command(name='join')
  async def command_join(ctx):
    if bot.queue.contains(ctx.author.name):
      await ctx.send(f"{ctx.author.name}, you are already in the queue!")
      return
    
    bot.queue.append(ctx.author.name)
    await ctx.send(f"{ctx.author.name} has been added to the queue!")

  @commands.command(name='next')
  async def command_next(ctx):
    if ctx.author.name != CHANNEL_NAME.lower():
      return
    
    if bot.queue.empty():
      await ctx.send("The queue is empty.")
      return

    next_user = bot.queue.pop()
    await ctx.send(f"Next in queue: {next_user}")

  @commands.command(name='leave')
  async def command_leave(ctx):
    if bot.queue.contains(ctx.author.name):
      bot.queue.remove(ctx.author.name)
      await ctx.send(f"{ctx.author.name} has left the queue!")
      return
    await ctx.send(f"{ctx.author.name} is not in the queue!")

  @commands.command(name='queue')
  async def command_queue(ctx):
    if bot.queue.empty():
      await ctx.send("The queue is empty.")
      return

    first_user = bot.queue.peek()

    if not bot.queue.contains(ctx.author.name):
      await ctx.send(f"{first_user} is 1st. {ctx.author.name}, you are not in the queue!")
      return 

    if ctx.author.name == first_user:
      await ctx.send(f"{ctx.author.name}, you are 1st in the queue!")
      return

    position = bot.queue.index(ctx.author.name) + 1
    await ctx.send(f"{first_user} is 1st. {ctx.author.name}, you are {to_ordinal(position)} in the queue!")

  @commands.command(name='position', aliases=['number'])
  async def command_position(ctx):
    if not bot.queue.contains(ctx.author.name):
      await ctx.send(f"{ctx.author.name}, you are not in the queue!")
      return
    
    position = bot.queue.index(ctx.author.name) + 1
    await ctx.send(f"{ctx.author.name}, you are {to_ordinal(position)} in the queue!")

  @commands.command(name='remove')
  async def command_remove(ctx, user: str):
    if not ctx.author.is_mod:
      return
    
    user = user.replace('@', '')
    user = user.lower()

    if not bot.queue.contains(user):
      await ctx.send(f"{user} is not in the queue!")
      return
    
    bot.queue.remove(user)
    await ctx.send(f"{user} has been removed from the queue!")

  bot.add_command(command_join)
  bot.add_command(command_next)
  bot.add_command(command_leave)
  bot.add_command(command_queue)
  bot.add_command(command_position)
  bot.add_command(command_remove)

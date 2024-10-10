from random import randint

from twitchio.ext import commands

from utils import CHANNEL_NAME


def setup_tag_commands(bot):

  @commands.command(name='tag')
  async def command_tag(ctx, user: str):
    user = user.replace('@', '')
    user = user.lower()

    if user == 'rexxauto' or ctx.author.name != bot.curr_tag:
      return
    
    if user == ctx.author.name:
      await ctx.send(f"{ctx.author.name}, you cannot tag yourself!")
      return
    
    if user in bot.failed_tags:
      await ctx.send(f"{ctx.author.name}, you already tried to tag {user}!")
      return
    
    channel = bot.get_channel(CHANNEL_NAME)
    chatter_names = [chatter.name for chatter in channel.chatters]
    
    if user not in chatter_names:
      await ctx.send(f"{user} is not in the channel!")
      return
    
    if randint(0,1):
      bot.curr_tag = user
      bot.failed_tags = []
      await ctx.send(f"{ctx.author.name} tags {user}!")
    else:
      bot.failed_tags.append(user)
      await ctx.send(f"{ctx.author.name} failed to tag {user}!")

  @commands.command(name='current')
  async def command_current(ctx):
    await ctx.send(bot.curr_tag)

  bot.add_command(command_tag)
  bot.add_command(command_current)

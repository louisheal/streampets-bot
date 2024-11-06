import json

from twitchio.ext import commands

from app.models import Color


def setup_pet_commands(bot):

  @commands.command(name='jump')
  async def command_jump(ctx):
    username = ctx.author.name
    bot.announcer.announce_jump(username)

  @commands.command(name='color')
  async def command_color(ctx, color):
    if color.lower() not in [c.name.lower() for c in Color]:
      await ctx.send(f"{color} is not an available color!")
      return
    
    username = ctx.author.name
    bot.db.set_trex_color(username, Color.str_to_color(color))
    bot.announcer.announce_color(username, color)

  bot.add_command(command_jump)
  bot.add_command(command_color)

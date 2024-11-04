import json

from twitchio.ext import commands

from app.models import Color
from app.consts import JUMP, COLOR


def setup_pet_commands(bot):

  @commands.command(name='jump')
  async def command_jump(ctx):
    bot.announcer.announce(msg=ctx.author.name, event=f'JUMP-{ctx.author.name}')

  @commands.command(name='color')
  async def command_color(ctx, color):
    if color.lower() not in [c.name.lower() for c in Color]:
      await ctx.send(f"{color} is not an available color!")
      return
    
    trex = bot.db.set_trex_color(ctx.author.name, Color.str_to_color(color))
    bot.announcer.announce(msg=json.dumps(trex.to_dict()), event=f'COLOR-{ctx.author.name}')

  bot.add_command(command_jump)
  bot.add_command(command_color)

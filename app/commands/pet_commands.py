from typing import TYPE_CHECKING

from twitchio.ext import commands

from app.config import ENVIRONMENT
from app.consts import PRODUCTION

if TYPE_CHECKING:
  from bot import ChatBot


class PetCommands(commands.Cog):

  def __init__(self, bot: commands.Bot) -> None:
    self.bot: 'ChatBot' = bot

  @commands.command(name='jump')
  async def command_jump(self, ctx):
    self.bot.announcer.announce_jump(ctx.author.id)

  @commands.command(name='color')
  async def command_color(self, ctx: commands.Context, color_name: str):
    user_id = ctx.author.id
    username = ctx.author.display_name

    colors = self.bot.db.get_colors()
    color = [color for color in colors if color.name.lower() == color_name.lower()]
    if not color:
      await ctx.send(f"{username} that is not an available color!")
      return

    if ENVIRONMENT == PRODUCTION:
      colors = self.bot.db.get_owned_colors(user_id)
      color = [color for color in colors if color.name.lower() == color_name.lower()]
      if not color:
        await ctx.send(f"{username} you do not own the color {color_name}!")
        return

    self.bot.db.set_current_color(user_id, color[0].id)
    self.bot.announcer.announce_color(user_id, color[0])

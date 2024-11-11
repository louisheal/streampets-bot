from typing import TYPE_CHECKING

from twitchio.ext import commands

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
    colors = self.bot.db.get_colors()
    user_id = ctx.author.id

    color = [color for color in colors if color.name.lower() == color_name.lower()]
    if not color:
      await ctx.send(f"{color_name} is not an available color!")
      return

    self.bot.db.set_current_color(user_id, color[0].id)
    self.bot.announcer.announce_color(user_id, color[0])

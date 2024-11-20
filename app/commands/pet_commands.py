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
  async def command_jump(self, ctx: commands.Context):
    channel_name = ctx.channel.name
    user_id = ctx.author.id
    self.bot.announcer.announce_jump(channel_name, user_id)

  @commands.command(name='color', aliases=['colour'])
  async def command_color(self, ctx: commands.Context, color_name: str):
    channel_name = ctx.channel.name
    channel_id = self.bot.db.get_channel_id(channel_name)

    user_id = ctx.author.id
    username = ctx.author.display_name

    color = self.bot.db.get_color_by_name(color_name)
    if not color:
      await ctx.send(f"{username} that is not an available color!")
      return

    if ENVIRONMENT == PRODUCTION:
      if not self.bot.db.user_owns_color(user_id, color.id):
        await ctx.send(f"{username} you do not own the color {color_name}!")
        return

    self.bot.db.set_current_color(user_id, channel_id, color[0].id)
    self.bot.announcer.announce_color(channel_name, user_id, color[0])

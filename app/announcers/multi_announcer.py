import queue

from app.announcers.channel_announcer import ChannelAnnouncer
from app.models import Color, Viewer


class MultiChannelAnnouncer():

  def __init__(self) -> None:
    self.announcers: dict[str, ChannelAnnouncer] = {}

  def listen(self, channel_name: str) -> queue.Queue:
    announcer = self.__get_announcer(channel_name)
    return announcer.listen()
  
  def announce_join(self, channel_name: str, viewer: Viewer) -> None:
    announcer = self.__get_announcer(channel_name)
    return announcer.announce_join(viewer)

  def announce_part(self, channel_name: str, user_id: str) -> None:
    announcer = self.__get_announcer(channel_name)
    return announcer.announce_part(user_id)

  def announce_color(self, channel_name: str, user_id: str, color: Color) -> None:
    announcer = self.__get_announcer(channel_name)
    return announcer.announce_color(user_id, color)

  def announce_jump(self, channel_name: str, user_id: str) -> None:
    announcer = self.__get_announcer(channel_name)
    return announcer.announce_jump(user_id)

  def __get_announcer(self, channel_name):
    if channel_name not in self.announcers:
      self.announcers[channel_name] = ChannelAnnouncer()
    return self.announcers[channel_name]

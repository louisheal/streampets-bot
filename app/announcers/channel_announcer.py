import json
import queue

from app.announcers.models import Event
from app.models import Color, Viewer


def format_sse(data: str, event: Event = None) -> str:
  msg = f'data: {data}\n\n'
  if event is not None:
    msg = f'event: {event}\n{msg}'
  return msg


class ChannelAnnouncer:

  def __init__(self) -> None:
    self.listeners: list[queue.Queue] = []

  def listen(self) -> queue.Queue:
    q = queue.Queue()
    self.listeners.append(q)
    return q
  
  def announce_join(self, viewer: Viewer) -> None:
    self.__announce(msg=json.dumps(viewer.to_dict()), event=Event.Join())

  def announce_part(self, user_id: str) -> None:
    self.__announce(msg=user_id, event=Event.Part())
  
  def announce_color(self, user_id: str, color: Color) -> None:
    self.__announce(msg=json.dumps(color.to_dict()), event=Event.Color(user_id))

  def announce_jump(self, user_id: str) -> None:
    self.__announce(msg=user_id, event=Event.Jump(user_id))

  def __announce(self, msg, event=None):
    msg = format_sse(msg, event)
    for i in reversed(range(len(self.listeners))):
      try:
        self.listeners[i].put_nowait(msg)
      except:
        del self.listeners[i]

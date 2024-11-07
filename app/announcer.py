import json
import queue

from app.models import Color, Viewer
from app.consts import (
  COLOR,
  JOIN,
  JUMP,
  PART,
)


def format_sse(data: str, event=None) -> str:
  msg = f'data: {data}\n\n'
  if event is not None:
    msg = f'event: {event}\n{msg}'
  return msg

class MessageAnnouncer:

  def __init__(self) -> None:
    self.listeners = []

  def listen(self):
    q = queue.Queue()
    self.listeners.append(q)
    return q
  
  def announce_part(self, user_id: str) -> None:
    self.__announce(msg=user_id, event=PART)
  
  def announce_color(self, user_id: str, color: Color) -> None:
    self.__announce(msg=color.name.lower(), event=f'{COLOR}-{user_id}')

  def announce_join(self, viewer: Viewer) -> None:
    msg = json.dumps(viewer.to_dict())
    self.__announce(msg=msg, event=JOIN)
  
  def announce_jump(self, user_id):
    # TODO: Message can be none
    self.__announce(msg=user_id, event=f'{JUMP}-{user_id}')

  def __announce(self, msg, event=None):
    msg = format_sse(msg, event)
    for i in reversed(range(len(self.listeners))):
      try:
        self.listeners[i].put_nowait(msg)
      except:
        del self.listeners[i]

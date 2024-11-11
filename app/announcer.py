import json
import queue

from app.models import Color, Viewer

JOIN  = 'JOIN'
PART  = 'PART'
JUMP  = 'JUMP'
COLOR = 'COLOR'


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
  
  def announce_join(self, viewer: Viewer) -> None:
    self.__announce(msg=json.dumps(viewer.to_dict()), event=JOIN)

  def announce_part(self, user_id: str) -> None:
    self.__announce(msg=user_id, event=PART)
  
  def announce_color(self, user_id: str, color: Color) -> None:
    self.__announce(msg=json.dumps(color.to_dict()), event=f'{COLOR}-{user_id}')

  def announce_jump(self, user_id: str) -> None:
    self.__announce(msg=user_id, event=f'{JUMP}-{user_id}')

  def __announce(self, msg, event=None):
    msg = format_sse(msg, event)
    for i in reversed(range(len(self.listeners))):
      try:
        self.listeners[i].put_nowait(msg)
      except:
        del self.listeners[i]

import json
import queue

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
  
  # TODO: username -> userID
  def announce_part(self, username):
    self.__announce(msg=username, event=PART)
  
  # TODO: username -> userID
  def announce_color(self, username, color):
    self.__announce(msg=color, event=f'{COLOR}-{username}')

  # TODO: username -> userID
  def announce_join(self, username, color):
    # TODO: encode (color, username, userID) into msg
    msg = json.dumps({'color': color, 'username': username})
    self.__announce(msg=msg, event=JOIN)
  
  # TODO: username -> userID
  def announce_jump(self, username):
    self.__announce(msg=username, event=f'{JUMP}-{username}')

  def __announce(self, msg, event=None):
    msg = format_sse(msg, event)
    for i in reversed(range(len(self.listeners))):
      try:
        self.listeners[i].put_nowait(msg)
      except:
        del self.listeners[i]

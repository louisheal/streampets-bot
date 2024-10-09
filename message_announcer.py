import queue

from utils import format_sse


class MessageAnnouncer:

  def __init__(self) -> None:
    self.listeners = []

  def listen(self):
    q = queue.Queue()
    self.listeners.append(q)
    return q
  
  def announce(self, msg, event=None):
    msg = format_sse(msg, event)
    for i in reversed(range(len(self.listeners))):
      try:
        self.listeners[i].put_nowait(msg)
      except:
        del self.listeners[i]

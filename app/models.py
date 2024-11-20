import time
from dataclasses import dataclass
from typing import Optional

from app.consts import LRU_LIMIT


@dataclass
class Color:
  id: int
  name: str
  img: str
  sku: str
  prev: str

  def to_dict(self):
    return {
      'id': self.id,
      'name': self.name,
      'img': self.img,
      'sku': self.sku,
      'prev': self.prev,
    }


@dataclass
class Viewer:
  user_id: str
  username: Optional[str] = None
  color: Optional[Color] = None

  def __eq__(self, other: object) -> bool:
    if isinstance(other, Viewer):
      return self.user_id == other.user_id
    return False

  def to_dict(self):
    return {
      'userID': self.user_id,
      'username': self.username,
      'color': self.color.to_dict(),
    }


class UserLRU:

  def __init__(self) -> None:
    # UserID -> Timestamp
    self.timestamps: dict[str,float] = {}
    # UserID -> Viewer
    self.viewers: dict[str,Viewer] = {}

  def add(self, viewer: Viewer) -> Optional[str]:
    '''Returns the id of the removed user, or None if no user was removed.'''
    timestamp = time.time()

    self.timestamps[viewer.user_id] = timestamp
    self.viewers[viewer.user_id] = viewer
    
    if len(self.viewers) > LRU_LIMIT:
      min_id, min_ts = viewer, timestamp
      for id, ts in self.timestamps.items():
        if ts < min_ts:
          min_id, min_ts = id, ts

      del self.timestamps[min_id]
      del self.viewers[min_id]

  def update_user(self, user_id: str) -> None:
    '''Updates the user's timestamp to the current time.'''
    self.timestamps[user_id] = time.time()

  def get_viewers(self) -> list[Viewer]:
    return list(self.viewers.values())

  def __contains__(self, user_id: str) -> bool:
    return user_id in self.timestamps

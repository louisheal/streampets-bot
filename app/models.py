from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Color(Enum):
  BLUE = 0
  BLACK = 1
  PURPLE = 2
  ORANGE = 3
  GREEN = 4
  RED = 5
  PINK = 6

  __color_map = {}

  @classmethod
  def _initialise_color_map(cls):
    cls.__color_map = {color.name.lower(): color for color in cls}

  @staticmethod
  def str_to_color(string):
    return Color.__color_map[string]

Color._initialise_color_map()


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
      'color': self.color.name.lower(),
    }

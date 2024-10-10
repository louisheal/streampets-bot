from dataclasses import dataclass

from models import Color


@dataclass
class TRex:
  username: str
  color: Color

  def to_dict(self):
    return {
      'username': self.username,
      'color': self.color.name.lower(),
    }

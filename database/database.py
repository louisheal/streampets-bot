import abc

from models import Color, TRex


class IDatabase(abc.ABC):

  @abc.abstractmethod
  def get_all_trexs(self, viewers: list[str]) -> list[TRex]:
    pass

  @abc.abstractmethod
  def get_trex_by_username(self, username: str) -> TRex:
    pass

  @abc.abstractmethod
  def set_trex_color(self, username: str, color: Color) -> TRex:
    pass

import abc


class SimpleQueue(abc.ABC):
  
  @abc.abstractmethod
  def append(self, item) -> None:
    pass

  @abc.abstractmethod
  def pop(self):
    pass

  @abc.abstractmethod
  def peek(self):
    pass

  @abc.abstractmethod
  def index(self, item) -> int:
    pass

  @abc.abstractmethod
  def remove(self, item) -> None:
    pass

  @abc.abstractmethod
  def contains(self, item) -> bool:
    pass

  @abc.abstractmethod
  def empty(self) -> bool:
    pass

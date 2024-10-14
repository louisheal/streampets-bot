import json
from typing import Generic, TypeVar


T = TypeVar('T')

class JsonQueue(Generic[T]):

  def __init__(self, path: str) -> None:
    self.path = path

  def append(self, item: T) -> None:
    queue = self.__load()
    queue.append(item)
    self.__save(queue)
  
  def pop(self) -> T:
    queue = self.__load()
    item = queue.pop(0)
    self.__save(queue)
    return item
    
  def peek(self) -> T:
    queue = self.__load()
    return queue[0]
    
  def index(self, item: T) -> int:
    queue = self.__load()
    return queue.index(item)
    
  def remove(self, item: T) -> None:
    queue = self.__load()
    queue.remove(item)
    self.__save(queue)
    
  def contains(self, item: T) -> bool:
    queue = self.__load()
    return item in queue
    
  def empty(self) -> bool:
    queue = self.__load()
    return not queue
    
  def __load(self) -> list[T]:
    with open(self.path, 'r') as f:
      return json.load(f)
    
  def __save(self, queue: list[T]) -> None:
    with open(self.path, 'w') as f:
      json.dump(queue, f)

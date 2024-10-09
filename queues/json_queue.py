import json

from .simple_queue import SimpleQueue


class JsonQueue(SimpleQueue):

  def __init__(self, path) -> None:
    self.path = path

  def append(self, item) -> None:
    queue = self.__load()
    queue.append(item)
    self.__save(queue)
  
  def pop(self):
    queue = self.__load()
    item = queue.pop(0)
    self.__save(queue)
    return item
    
  def peek(self):
    queue = self.__load()
    return queue[0]
    
  def index(self, item) -> int:
    queue = self.__load()
    return queue.index(item)
    
  def remove(self, item) -> None:
    queue = self.__load()
    queue.remove(item)
    self.__save(queue)
    
  def contains(self, item) -> bool:
    queue = self.__load()
    return item in queue
    
  def empty(self) -> bool:
    queue = self.__load()
    return not queue
    
  def __load(self):
    with open(self.path, 'r') as f:
      return json.load(f)
    
  def __save(self, queue):
    with open(self.path, 'w') as f:
      json.dump(queue, f)

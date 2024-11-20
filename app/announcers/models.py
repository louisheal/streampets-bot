from enum import Enum


class EventType(Enum):
  JOIN  = 'JOIN'
  PART  = 'PART'
  JUMP  = 'JUMP'
  COLOR = 'COLOR'

class Event():
  
  def __init__(self, event_type: EventType, user_id: str = None) -> None:
    self.event_type = event_type
    self.user_id = user_id

  @classmethod
  def Join(cls):
    return Event(EventType.JOIN)
  
  @classmethod
  def Part(cls):
    return Event(EventType.PART)
  
  @classmethod
  def Jump(cls, user_id: str):
    return Event(EventType.JUMP, user_id)
  
  @classmethod
  def Color(cls, user_id: str):
    return Event(EventType.COLOR, user_id)

  def __str__(self) -> str:
    if self.event_type in [EventType.COLOR, EventType.JUMP]:
      return f"{self.event_type.value}-{self.user_id}"
    return self.event_type.value

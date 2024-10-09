from trex import TRex


class Database():

  def __init__(self) -> None:
    pass

  def get_all_rexs(self, viewers: list[str]) -> list[TRex]:
    result = []
    for viewer in viewers:
      if viewer == 'ljrexcodes':
        result.append(TRex(viewer, 'blue'))
      else:
        result.append(TRex(viewer, 'green'))
    return result

  def get_rex_by_username(self, username: str) -> TRex:
    if username == 'ljrexcodes':
      return TRex(username, 'blue')
    return TRex(username, 'green')

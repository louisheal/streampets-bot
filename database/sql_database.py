import sqlite3

from database import IDatabase
from models import TRex, Color


class SqlDatabase(IDatabase):

  def __init__(self, db_path) -> None:
    self.db_path = db_path

  def get_all_rexs(self, viewers: list[str]) -> list[TRex]:
    return [self.get_trex_by_username(username) for username in viewers]
  
  def get_trex_by_username(self, username: str) -> TRex:
    connection = sqlite3.connect(self.db_path)
    cursor = connection.cursor()
    
    cursor.execute(f"SELECT username, colorID FROM trexs WHERE username=?", (username,))
    result = cursor.fetchone()

    if not result:
      return TRex(username, Color.GREEN)
    
    username, color = result
    return TRex(username, Color(color))
  
  def set_trex_color(self, username: str, color: Color) -> TRex:
    connection = sqlite3.connect(self.db_path)
    cursor = connection.cursor()

    cursor.execute("INSERT OR REPLACE INTO trexs (username, colorID) VALUES (?,?)", (username, color.value))
    connection.commit()

    return TRex(username, color)
  

  # TREXS
  # username | color
  # ljrexcodes   1
  # moxisbae     0

  # COLORS
  # id | color
  # 0    black
  # 1    blue

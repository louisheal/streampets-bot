import libsql_client

from app.models import Color, TRex


class Database():

  def __init__(self, token, url) -> None:
    self.token = token
    self.url = url

  # TODO: usernames -> userIDs
  # TODO: ordered list Color[] / dict[userID][Color]
  def get_all_trexs(self, usernames: list[str]) -> list[TRex]:
    return [self.get_trex_by_username(username) for username in usernames]

  # TODO: get color by userID
  def get_trex_by_username(self, username: str) -> TRex:
    with libsql_client.create_client_sync(self.url, auth_token=self.token) as client:
      result_set = client.execute("SELECT username, colorID FROM trexs WHERE username=?", (username,))
      
      if not result_set:
        return TRex(username, Color.GREEN)

      username, color = result_set.rows[0]
      return TRex(username, Color(color))

  # TODO: set color of userID
  def set_trex_color(self, username: str, color: Color) -> TRex:
    with libsql_client.create_client_sync(self.url, auth_token=self.token) as client:
      client.execute("INSERT OR REPLACE INTO trexs (username, colorID) VALUES (?,?)", (username, color.value))
    return TRex(username, color)

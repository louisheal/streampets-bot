import libsql_client

from app.models import Color


class Database():

  def __init__(self, token: str, url: str) -> None:
    self.token = token
    self.url = url

  def get_color_by_user_id(self, user_id: str) -> Color:
    with libsql_client.create_client_sync(self.url, auth_token=self.token) as client:
      result_set = client.execute("SELECT colorID FROM viewers WHERE userID=?", (user_id,))
      return Color.GREEN if not result_set else Color(result_set.rows[0][0])

  def set_color_by_user_id(self, user_id: str, color: Color) -> None:
    with libsql_client.create_client_sync(self.url, auth_token=self.token) as client:
      client.execute("INSERT OR REPLACE INTO viewers (userID, colorID) VALUES (?,?)", (user_id, color.value))

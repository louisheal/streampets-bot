import libsql_client

from app.models import Color


GREEN = Color(4, 'Green', '#0F0', 'assets/green-rex.png')

GET_CURRENT_COLOR_QUERY = '''
  SELECT colors.id, colors.name, colors.hex, colors.img
  FROM colors
  WHERE colors.id = (SELECT colorID FROM viewers WHERE userID = ?);
'''
SET_CURRENT_COLOR_QUERY = '''
  INSERT OR REPLACE INTO viewers (userID, colorID) VALUES (?,?)
'''
GET_OWNED_COLORS_QUERY = '''
  SELECT colors.id, colors.name, colors.hex, colors.img
  FROM (SELECT colorID FROM owned_colors WHERE userID = ?) AS new_owned_colors
  JOIN colors ON colors.id = new_owned_colors.colorID
'''
GET_COLORS_QUERY = '''
  SELECT id, name, hex, img
  FROM colors
'''

class Database():

  def __init__(self, token: str, url: str) -> None:
    self.token = token
    self.url = url

  def get_colors_by_user_ids(self, user_ids: list[str]) -> list[Color]:
    return [self.get_current_color(user_id) for user_id in user_ids]

  def get_current_color(self, user_id: str) -> Color:
    with libsql_client.create_client_sync(self.url, auth_token=self.token) as client:
      result_set = client.execute(GET_CURRENT_COLOR_QUERY, (user_id,))
      if not result_set:
        return GREEN

      row = result_set.rows[0]
      return Color(row[0], row[1], row[2], row[3])

  def set_current_color(self, user_id: str, color_id: int) -> None:
    with libsql_client.create_client_sync(self.url, auth_token=self.token) as client:
      client.execute(SET_CURRENT_COLOR_QUERY, (user_id, color_id))

  def get_owned_colors(self, user_id: str) -> list[Color]:
    with libsql_client.create_client_sync(self.url, auth_token=self.token) as client:
      result = client.execute(GET_OWNED_COLORS_QUERY, (user_id,))
      return [Color(row[0], row[1], row[2], row[3]) for row in result.rows] + [GREEN]

  def get_colors(self) -> list[Color]:
    with libsql_client.create_client_sync(self.url, auth_token=self.token) as client:
      result = client.execute(GET_COLORS_QUERY)
      return [Color(row[0], row[1], row[2], row[3]) for row in result.rows] + [GREEN]

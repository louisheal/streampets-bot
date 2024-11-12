import libsql_client

from app.models import Color


GREEN = Color(4, 'Green', '#0F0', 'assets/green-rex.png', 'C4')

GET_CURRENT_COLOR_QUERY = '''
  SELECT colors.*
  FROM colors
  WHERE colors.id = (SELECT colorID FROM viewers WHERE userID = ?);
'''
SET_CURRENT_COLOR_QUERY = '''
  INSERT OR REPLACE INTO viewers (userID, colorID) VALUES (?,?)
'''
GET_OWNED_COLORS_QUERY = '''
  SELECT colors.*
  FROM (SELECT colorID FROM owned_colors WHERE userID = ?) AS new_owned_colors
  JOIN colors ON colors.id = new_owned_colors.colorID
'''
ADD_OWNED_COLOR_QUERY = '''
  INSERT INTO owned_colors (userID, colorID) VALUES (?,?)
'''
GET_COLORS_QUERY = '''
  SELECT id, name, hex, img
  FROM colors
'''
GET_COLOR_BY_SKU_QUERY = '''
  SELECT colors.id
  FROM colors
  WHERE colors.sku = ?
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
      return row_to_color(row)

  def set_current_color(self, user_id: str, color_id: int) -> None:
    with libsql_client.create_client_sync(self.url, auth_token=self.token) as client:
      client.execute(SET_CURRENT_COLOR_QUERY, (user_id, color_id))

  def get_owned_colors(self, user_id: str) -> list[Color]:
    with libsql_client.create_client_sync(self.url, auth_token=self.token) as client:
      result = client.execute(GET_OWNED_COLORS_QUERY, (user_id,))
      return [row_to_color(row) for row in result.rows] + [GREEN]
  
  def add_owned_color(self, user_id: str, color_id: str) -> None:
    with libsql_client.create_client_sync(self.url, auth_token=self.token) as client:
      client.execute(ADD_OWNED_COLOR_QUERY, (user_id, color_id))

  def get_colors(self) -> list[Color]:
    with libsql_client.create_client_sync(self.url, auth_token=self.token) as client:
      result = client.execute(GET_COLORS_QUERY)
      return [row_to_color(row) for row in result.rows] + [GREEN]

  # TODO: Make custom error (invalid sku) and raise
  def get_color_id_by_sku(self, sku: str) -> str:
    '''Raises an exception if sku is invalid'''
    with libsql_client.create_client_sync(self.url, auth_token=self.token) as client:
      result = client.execute(GET_COLOR_BY_SKU_QUERY, (sku,))
      return result.rows[0][0]
    
def row_to_color(row) -> Color:
  return Color(row[0], row[1], row[2], row[3], row[4])

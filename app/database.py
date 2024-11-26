from typing import Optional
import secrets

import libsql_client

from app.models import Color
from app.consts import GREEN_ID


GET_CURRENT_COLOR_QUERY = '''
  SELECT Colors.*
  FROM Colors
  WHERE Colors.id = (SELECT ColorID FROM SelectedColors WHERE UserID = ? AND ChannelID = ?);
'''
SET_CURRENT_COLOR_QUERY = '''
  INSERT OR REPLACE INTO SelectedColors (UserID, ChannelID, ColorID)
  VALUES (?,?,?)
'''
GET_OWNED_COLORS_QUERY = '''
  SELECT Colors.*
  FROM (SELECT ColorID FROM OwnedColors WHERE UserID = ? AND ChannelID = ?) AS owned_colors
  JOIN Colors ON Colors.id = owned_colors.colorID
'''
ADD_OWNED_COLOR_QUERY = '''
  INSERT INTO OwnedColors (ChannelID, UserID, ColorID, TransactionID)
  VALUES (?,?,?,?)
'''
GET_COLORS_QUERY = '''
  SELECT *
  FROM Colors
'''
GET_COLOR_BY_NAME_QUERY = '''
  SELECT *
  FROM Colors
  WHERE name = ?
'''
GET_CHANNEL_ID_QUERY = '''
  SELECT ChannelID
  FROM Channels
  WHERE ChannelName = ?
'''
GET_CHANNEL_NAME_QUERY = '''
  SELECT ChannelName
  FROM Channels
  WHERE ChannelID = ?
'''
UPDATE_CHANNEL_NAME_QUERY = '''
  UPDATE Channels
  SET ChannelName = ?
  WHERE ChannelID = ?
'''
GET_OVERLAY_ID_QUERY = '''
  SELECT OverlayID
  FROM Channels
  WHERE ChannelID = ?
'''
ADD_OVERLAY_ID_QUERY = '''
  INSERT INTO Channels (ChannelID, OverlayID) VALUES (?,?)
'''
USER_OWNS_COLOR_QUERY = '''
  SELECT *
  FROM OwnedColors
  WHERE UserID = ? AND ColorID = ?
'''


class Database():

  def __init__(self, token: str, url: str) -> None:
    self.token = token
    self.url = url

  def get_colors_by_user_ids(self, user_ids: list[str], channel_id: str) -> list[Color]:
    return [self.get_current_color(user_id, channel_id) for user_id in user_ids]

  def get_current_color(self, user_id: str, channel_id: str) -> Color:
    with libsql_client.create_client_sync(self.url, auth_token=self.token) as client:
      result_set = client.execute(GET_CURRENT_COLOR_QUERY, (user_id,channel_id))
      if not result_set:
        self.set_current_color(user_id, channel_id, GREEN_ID)
        result_set = client.execute(GET_CURRENT_COLOR_QUERY, (user_id,channel_id))
      row = result_set.rows[0]
      return row_to_color(row)

  def set_current_color(self, user_id: str, channel_id: str, color_id: int) -> None:
    with libsql_client.create_client_sync(self.url, auth_token=self.token) as client:
      client.execute(SET_CURRENT_COLOR_QUERY, (user_id, channel_id, color_id))

  def get_owned_colors(self, user_id: str, channel_id: str) -> list[Color]:
    with libsql_client.create_client_sync(self.url, auth_token=self.token) as client:
      result = client.execute(GET_OWNED_COLORS_QUERY, (user_id,channel_id))
      if not result:
        transaction_id = secrets.token_hex(16)
        self.add_owned_color(user_id, channel_id, GREEN_ID, transaction_id)
        result = client.execute(GET_OWNED_COLORS_QUERY, (user_id,channel_id))
      return [row_to_color(row) for row in result.rows]
  
  def add_owned_color(self, user_id: str, channel_id: str, color_id: str, transaction_id: str) -> None:
    with libsql_client.create_client_sync(self.url, auth_token=self.token) as client:
      print(user_id, channel_id, color_id, transaction_id)
      client.execute(ADD_OWNED_COLOR_QUERY, (channel_id, user_id, color_id, transaction_id))

  def get_colors(self) -> list[Color]:
    with libsql_client.create_client_sync(self.url, auth_token=self.token) as client:
      result = client.execute(GET_COLORS_QUERY)
      return [row_to_color(row) for row in result.rows]
    
  def get_color_by_name(self, color_name: str) -> Optional[Color]:
    with libsql_client.create_client_sync(self.url, auth_token=self.token) as client:
      result = client.execute(GET_COLOR_BY_NAME_QUERY, (color_name.capitalize(),))
      if not result.rows:
        return None
      return row_to_color(result.rows[0])
    
  # TODO: Handle case when channel name not found
  def get_channel_id(self, channel_name: str) -> str:
    with libsql_client.create_client_sync(self.url, auth_token=self.token) as client:
      result = client.execute(GET_CHANNEL_ID_QUERY, (channel_name,))
      return result.rows[0][0]
    
  def get_channel_name(self, channel_id: str) -> str:
    with libsql_client.create_client_sync(self.url, auth_token=self.token) as client:
      result = client.execute(GET_CHANNEL_NAME_QUERY, (channel_id,))
      return result.rows[0][0]
    
  def update_channel_name(self, channel_id: str, channel_name: str):
    with libsql_client.create_client_sync(self.url, auth_token=self.token) as client:
      client.execute(UPDATE_CHANNEL_NAME_QUERY, (channel_name, channel_id))
    
  def get_overlay_id(self, channel_id: str) -> str:
    '''Returns the overlay id associated with the channel id.
    Or creates one if it does not exist.'''
    with libsql_client.create_client_sync(self.url, auth_token=self.token) as client:
      result = client.execute(GET_OVERLAY_ID_QUERY, (channel_id,))
      if result.rows:
        return result.rows[0][0]
      overlay_id = secrets.token_hex(16)
      client.execute(ADD_OVERLAY_ID_QUERY, (channel_id,overlay_id))
      return overlay_id
    
  def user_owns_color(self, user_id: str, color_id: str) -> bool:
    with libsql_client.create_client_sync(self.url, auth_token=self.token) as client:
      result = client.execute(USER_OWNS_COLOR_QUERY, (user_id, color_id))
      return len(result.rows) > 0

def row_to_color(row) -> Color:
  return Color(row[0], row[1], row[2], row[3], row[4])

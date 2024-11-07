import requests

from app.config import (
  CLIENT_ID,
  CLIENT_SECRET
)

def get_user_id_by_username(username):
  access_token = __access_token()
  return requests.get('https://api.twitch.tv/helix/users',
    params={'login': username},
    headers={
      'Authorization': f'Bearer {access_token}',
      'Client-ID': CLIENT_ID,
  }).json()['data'][0]['id']

def get_usernames_by_user_ids(user_ids: list[str]):
  if not user_ids:
    return []
  params = '&'.join([f'id={user_id}' for user_id in user_ids])
  access_token = __access_token()
  data = requests.get('https://api.twitch.tv/helix/users',
    params=params,
    headers={
      'Authorization': f'Bearer {access_token}',
      'Client-ID': CLIENT_ID,
  }).json()['data']
  return [user['login'] for user in data]

def __access_token():
  return requests.post('https://id.twitch.tv/oauth2/token', data={
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
    'grant_type': 'client_credentials',
  }).json()['access_token']

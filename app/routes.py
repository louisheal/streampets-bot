import base64
import requests

from fastapi import APIRouter, Request, Response, status
from fastapi.responses import StreamingResponse
from jose import jwt

from app.models import Color, Viewer
from app import announcer, bot, database

from app.config import (
  CLIENT_ID,
  CLIENT_SECRET,
  EXT_SECRET
)


router = APIRouter()

@router.get('/listen')
async def listen():
  def stream():
    messages = announcer.listen()
    while True:
      msg = messages.get()
      yield msg
  return StreamingResponse(stream(), media_type='text/event-stream')

@router.get('/viewers')
async def get_viewers():
  user_ids = bot.get_user_ids()
  viewers = []
  for user_id in user_ids:
    username = get_username_by_user_id(user_id)
    color = database.get_color_by_user_id(user_id)
    viewers.append(Viewer(user_id, username, color))
  
  return viewers

@router.get('/colors')
async def get_colors():
  return [color.name.lower() for color in Color]

@router.put('/colors')
async def update_color(request: Request):
  jwt_data = decode_jwt(request.headers.get('x-extension-jwt'))
  user_id = jwt_data['user_id']

  data = await request.json()
  color = Color.str_to_color(data['color'])

  database.set_color_by_user_id(user_id, color)
  announcer.announce_color(user_id, color)

  return Response(status_code=status.HTTP_200_OK)

@router.get('/user')
def get_user_data(request: Request):
  jwt_data = decode_jwt(request.headers.get('x-extension-jwt'))
  user_id = jwt_data['user_id']

  color = database.get_color_by_user_id(user_id)

  # TODO: JSON format color ???
  return color

def decode_jwt(token):
  # TODO: Do this at startup ???
  key = base64.b64decode(EXT_SECRET)
  return jwt.decode(token, key)

def __access_token():
  response = requests.post('https://id.twitch.tv/oauth2/token', data={
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
    'grant_type': 'client_credentials',
  }).json()
  return response.get('access_token')

def get_username_by_user_id(user_id):
  access_token = __access_token()
  return requests.get('https://api.twitch.tv/helix/users',
    params={'id': user_id},
    headers={
      'Authorization': f'Bearer {access_token}',
      'Client-ID': CLIENT_ID,
  }).json()['data'][0]['login']

import base64
import json

from dataclasses import dataclass, asdict
from fastapi import APIRouter, Request, Response, status
from fastapi.responses import StreamingResponse
from jose import jwt
import requests

from app.models import Color
from app import announcer, bot, database

from app.config import (
  CLIENT_ID,
  CLIENT_SECRET,
  EXT_SECRET,
)


# TODO: Move to models.py
@dataclass
class TwitchUser:
   id: str
   username: str
   profile_pic: str
   color: str

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
async def viewers():
  rexs = bot.get_viewer_rexs()
  json_rexs = [rex.to_dict() for rex in rexs]
  return json_rexs

@router.get('/colors')
async def get_colors():
  colors = [color.name.lower() for color in Color]
  return colors

@router.put('/colors')
async def update_color(request: Request):
  jwt_data = decode_jwt(request.headers.get('x-extension-jwt'))

  user_id = jwt_data['user_id']
  user_data = get_user_data_by_user_id(user_id)

  username = user_data['display_name'].lower()

  data = await request.json()
  color = Color.str_to_color(data['color'])
  trex = database.set_trex_color(username, color)
  # TODO: Move event name handling to central location
    # announcer.color_event(username, color)
  announcer.announce(msg=json.dumps(trex.to_dict()), event=f'COLOR-{username}')
  return Response(status_code=status.HTTP_200_OK)

@router.get('/user')
def get_user_data(request: Request):
  jwt_data = decode_jwt(request.headers.get('x-extension-jwt'))

  user_id = jwt_data['user_id']
  user_data = get_user_data_by_user_id(user_id)

  username = user_data['display_name'].lower()
  profile_pic = user_data['profile_image_url']

  rex = database.get_trex_by_username(username)
  return asdict(TwitchUser(user_id,username,profile_pic,rex.color.name.lower()))

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

def get_user_data_by_user_id(user_id):
  access_token = __access_token()
  return requests.get('https://api.twitch.tv/helix/users',
    params={'id': user_id},
    headers={
      'Authorization': f'Bearer {access_token}',
      'Client-ID': CLIENT_ID,
  }).json()['data'][0]

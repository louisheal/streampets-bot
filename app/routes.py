import json
from jose import jwt
import base64

from fastapi import APIRouter, Request, Response, status
from fastapi.responses import StreamingResponse

from app.models import Color
from app import announcer, bot, database

import os
import requests
from dataclasses import dataclass, asdict
from dotenv import load_dotenv

@dataclass
class TwitchUser:
   id: str
   username: str
   profile_pic: str
   color: str

load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')
STORE_URL = os.getenv('STORE_URL')
DOMAIN = os.getenv('DOMAIN')
EXT_SECRET = os.getenv('EXT_SECRET')


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

# receive jwt token
# verify and retrieve userID
# retrieve username
# set trex color
# announce color change

@router.put('/colors')
async def update_color(request: Request):
  jwt_token = request.headers.get('x-extension-jwt')
  # TODO: Is this worth doing on startup ?
  key = base64.b64decode(EXT_SECRET)
  jwt_data = jwt.decode(jwt_token, key)

  user_id = jwt_data['user_id']
  access_token = get_access_token()

  response = requests.get('https://api.twitch.tv/helix/users',
                          params={'id': user_id},
                          headers={
                            'Authorization': f'Bearer {access_token}',
                            'Client-ID': CLIENT_ID,
                          })
  user_data = response.json()['data'][0]

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
  jwt_token = request.headers.get('x-extension-jwt')
  key = base64.b64decode(EXT_SECRET)
  jwt_data = jwt.decode(jwt_token, key)

  user_id = jwt_data['user_id']
  access_token = get_access_token()

  response = requests.get('https://api.twitch.tv/helix/users',
                          params={'id': user_id},
                          headers={
                            'Authorization': f'Bearer {access_token}',
                            'Client-ID': CLIENT_ID,
                          })
  user_data = response.json()['data'][0]

  username = user_data['display_name'].lower()
  profile_pic = user_data['profile_image_url']

  rex = database.get_trex_by_username(username)
  return asdict(TwitchUser(user_id,username,profile_pic,rex.color.name.lower()))

def get_access_token():
  response = requests.post('https://id.twitch.tv/oauth2/token', data={
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
    'grant_type': 'client_credentials',
  }).json()

  return response.get('access_token')

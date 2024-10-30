import json

from fastapi import APIRouter, Cookie, HTTPException, Request, Response, status
from fastapi.responses import StreamingResponse, RedirectResponse

from app.models import Color
from app import announcer, bot, database

import os
import logging
import requests
import secrets
from typing import Optional
from dataclasses import dataclass, asdict
from dotenv import load_dotenv

@dataclass
class TwitchUser:
   id: str
   username: str
   profile_pic: str

load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')
STORE_URL = os.getenv('STORE_URL')

sessions = {}


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
  data = await request.json()
  session_id = request.cookies.get('session_id')
  username = sessions[session_id].username.lower()
  color = Color.str_to_color(data['color'])
  trex = database.set_trex_color(username, color)
  announcer.announce(msg=json.dumps(trex.to_dict()), event='COLOR')
  return Response(status_code=status.HTTP_200_OK)

@router.get('/auth/twitch')
def auth_twitch():
  oauth_state = secrets.token_hex(16)
  response = RedirectResponse(get_auth_url(oauth_state))
  response.set_cookie('oauth_state', oauth_state, path='/')
  return response

@router.get('/callback')
def callback(request: Request, state = None, code = None):
  response = RedirectResponse(STORE_URL)

  oauth_state = request.cookies.get('oauth_state')
  if state is None or state != oauth_state:
    logging.critical("Endpoint /callback accessed with incorrect state")
    return HTTPException(400, detail="State mismatch error")
  response.delete_cookie('oauth_state')

  if not code:
    logging.critical("Endpoint /callback accessed without code")
    return HTTPException(400, detail="Missing code parameter")

  twitch_user = get_user(code)
  print(twitch_user)
  if twitch_user is None:
    logging.critical("Endpoint /callback accessed with invalid code")
    return HTTPException(401, detail="Invalid Twitch access token")

  session_id = secrets.token_hex(16)
  response.set_cookie('session_id', session_id, path='/')
  sessions[session_id] = twitch_user

  print(sessions)

  logging.info(f"User {twitch_user.id} has successfully logged in")
  return response

@router.get('/logout')
def logout(response: Response, session_id = Cookie(None)):
  twitch_user = sessions.pop(session_id, None)
  response.delete_cookie('session_id')
  logging.info(f"{twitch_user.id} has been logged out")
  return {'message': f"{twitch_user.username}_logged_out"}

@router.get('/user')
def get_user_from_session_id(request: Request, response: Response):
  session_id = request.cookies.get('session_id')

  if session_id is None:
    return None
  
  if session_id not in sessions:
    response.delete_cookie('session_id')
    return None
  
  return asdict(sessions[session_id])

def get_auth_url(state):
  return (f"https://id.twitch.tv/oauth2/authorize?client_id={CLIENT_ID}&force_verify=true&redirect_uri={REDIRECT_URI}"
          f"&response_type=code&scope=user:read:email&state={state}")

def get_user(code) -> Optional[TwitchUser]:
  token_response = requests.post('https://id.twitch.tv/oauth2/token', params={
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
    'code': code,
    'grant_type': 'authorization_code',
    'redirect_uri': REDIRECT_URI,
  }).json()

  access_token = token_response.get('access_token')
  if not access_token:
    return None

  user_response = requests.get('https://api.twitch.tv/helix/users', headers={
    'Client-ID': CLIENT_ID,
    'Authorization': f'Bearer {access_token}'
  }).json()

  user_data = user_response['data'][0]
  return TwitchUser(user_data['id'], user_data['display_name'], user_data['profile_image_url'])

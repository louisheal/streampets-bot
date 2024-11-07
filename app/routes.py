import base64

from fastapi import APIRouter, Request, Response, status
from fastapi.responses import StreamingResponse
from jose import jwt

from app.models import Color, Viewer
from app.helix import get_usernames_by_user_ids
from app import announcer, bot, database

from app.config import EXT_SECRET


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
  usernames = get_usernames_by_user_ids(user_ids)
  colors = database.get_colors_by_user_ids(user_ids)
  return [Viewer(user_id, username, color).to_dict() for user_id, username, color in zip(user_ids, usernames, colors)]

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

import base64

from dataclasses import asdict
from fastapi import APIRouter, Request, Response, status
from fastapi.responses import StreamingResponse
from jose import jwt

from app.models import Color
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
async def viewers():
  viewers = bot.get_viewers()
  json_viewers = [viewer.to_dict() for viewer in viewers]
  return json_viewers

@router.get('/colors')
async def get_colors():
  colors = [color.name.lower() for color in Color]
  return colors

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

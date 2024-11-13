import base64

from fastapi import APIRouter, Request, Response, status
from fastapi.responses import StreamingResponse
from jose import jwt

from app.models import Viewer
from app.helix import get_usernames_by_user_ids
from app import announcer, bot, database
from app.config import EXT_SECRET


router = APIRouter()

#########################
### OVERLAY ENDPOINTS ###

@router.get('/listen')
async def listen():
  '''Called by Overlay on startup'''
  def stream():
    messages = announcer.listen()
    while True:
      msg = messages.get()
      yield msg
  return StreamingResponse(stream(), media_type='text/event-stream')

@router.get('/viewers')
async def get_viewers():
  '''Called by Overlay on startup'''
  user_ids = bot.get_user_ids()
  usernames = get_usernames_by_user_ids(user_ids)
  colors = database.get_colors_by_user_ids(user_ids)
  return [
    Viewer(user_id, username, color).to_dict()
    for user_id, username, color
    in zip(user_ids, usernames, colors)
  ]

###########################
### EXTENSION ENDPOINTS ###

@router.put('/colors')
async def update_color(request: Request):
  '''Called by Store on color change'''
  jwt_data = decode_jwt(request.headers.get('x-extension-jwt'))
  user_id = jwt_data['user_id']

  data = await request.json()
  color_id = data['color_id']

  database.set_current_color(user_id, color_id)
  color = database.get_current_color(user_id)
  announcer.announce_color(user_id, color)

  return Response(status_code=status.HTTP_200_OK)

@router.get('/user')
def get_user_data(request: Request):
  '''Called by Store on startup'''
  jwt_data = decode_jwt(request.headers.get('x-extension-jwt'))
  user_id = jwt_data['user_id']

  color = database.get_current_color(user_id)
  colors = database.get_owned_colors(user_id)

  # TODO: Turn this into a UserData dataclass
  return {
    'colors': {
      # TODO: Should return a url to the TRex image
      'current': color.to_dict(),
      'available': [color.to_dict() for color in colors]
    },
  }

@router.get('/store')
def get_store_items():
  '''Called by store on startup'''
  return {
    'colors': database.get_colors()
  }

@router.post('/store')
async def buy_item(request: Request):
  '''Called by Store onTransactionComplete'''
  data = await request.json()
  jwt_data = decode_jwt(data['token'])['data']

  user_id = jwt_data['userId']
  color_id = database.get_color_id_by_sku(jwt_data['product']['sku'])
  database.add_owned_color(user_id, color_id)

def decode_jwt(token):
  # TODO: Do this at startup ???
  key = base64.b64decode(EXT_SECRET)
  return jwt.decode(token, key)

###########################
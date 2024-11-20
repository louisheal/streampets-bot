import base64

from fastapi import APIRouter, Request, Response, status
from fastapi.responses import StreamingResponse
from jose import jwt

from app import announcer, bot, database
from app.helix import get_usernames_by_user_ids
from app.config import (
  EXT_SECRET,
  OVERLAY_URL,
)


router = APIRouter()

#########################
### OVERLAY ENDPOINTS ###

@router.get('/listen')
async def listen(overlayID: str, channelID: str):
  '''Called by Overlay on startup'''
  if overlayID != database.get_overlay_id(channelID):
    return Response(status_code=status.HTTP_403_FORBIDDEN)
  channel_name = get_usernames_by_user_ids([channelID])[0]
  database.update_channel_name(channelID, channel_name)

  await bot.join_channels([channel_name])
  
  def stream():
    messages = announcer.listen(channel_name)
    while True:
      msg = messages.get()
      yield msg

  return StreamingResponse(stream(), media_type='text/event-stream')

@router.get('/viewers')
async def get_viewers(overlayID: str, channelID: str):
  '''Called by Overlay on startup'''
  if overlayID != database.get_overlay_id(channelID):
    return Response(status_code=status.HTTP_403_FORBIDDEN)
  
  channel_name = get_usernames_by_user_ids([channelID])[0]
  database.update_channel_name(channelID, channel_name)
  
  return [viewer.to_dict() for viewer in bot.get_users(channel_name)]

###########################
### EXTENSION ENDPOINTS ###

@router.put('/colors')
async def update_color(request: Request):
  '''Called by Store on color change'''
  jwt_data = decode_jwt(request.headers.get('x-extension-jwt'))
  user_id = jwt_data['user_id']
  channel_id = jwt_data['channel_id']

  data = await request.json()
  color_id = data['color_id']

  # TODO: Check user owns color_id

  database.set_current_color(user_id, channel_id, color_id)
  color = database.get_current_color(user_id, channel_id)
  announcer.announce_color(user_id, color)

  return Response(status_code=status.HTTP_200_OK)

@router.get('/user')
def get_user_data(request: Request):
  '''Called by Store on startup'''
  jwt_data = decode_jwt(request.headers.get('x-extension-jwt'))
  user_id = jwt_data['user_id']
  channel_id = jwt_data['channel_id']

  color = database.get_current_color(user_id, channel_id)
  colors = database.get_owned_colors(user_id, channel_id)

  # TODO: Turn this into a UserData dataclass
  return {
    'colors': {
      'current': color.to_dict(),
      'available': [color.to_dict() for color in colors]
    },
  }

@router.get('/store')
def get_store_items():
  '''Called by store on startup'''
  return {'colors': database.get_colors()}

@router.post('/store')
async def buy_item(request: Request):
  '''Called by Store onTransactionComplete'''
  jwt_data = decode_jwt(request.headers.get('x-extension-jwt'))
  data = await request.json()
  receipt_data = decode_jwt(data['receipt'])['data']

  transaction_id = receipt_data['transactionId']

  # TODO: Remove, verify in DB (TransactionID: unique=True)
  if not database.verify_transaction(transaction_id):
    return

  color_id = data['color_id']
  user_id = receipt_data['userId']
  channel_id = jwt_data['channel_id']

  # TODO: Test that this function fails when transaction_id already exists
  database.add_owned_color(user_id, channel_id, color_id, transaction_id)

#############################
### Config.html Endpoints ###

@router.get('/overlayUrl')
async def get_overlay_url(request: Request):
  jwt_data = decode_jwt(request.headers.get('x-extension-jwt'))
  channel_id = jwt_data['channel_id']

  overlay_id = database.get_overlay_id(channel_id)

  # TODO: Move url prefix to .env
  return f"{OVERLAY_URL}?overlayID={overlay_id}&channelID={channel_id}"

###########################
########## Utils ##########

def decode_jwt(token):
  # TODO: Do this at startup ???
  key = base64.b64decode(EXT_SECRET)
  return jwt.decode(token, key)

###########################
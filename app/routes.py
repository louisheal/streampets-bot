import json

from fastapi import APIRouter, Request, Response, status
from fastapi.responses import StreamingResponse

from app.models import Color
from app import announcer, bot, database


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
  color = Color.str_to_color(data['color'])
  trex = database.set_trex_color('ljrexcodes', color)
  announcer.announce(msg=json.dumps(trex.to_dict()), event='COLOR')
  return Response(status_code=status.HTTP_200_OK)

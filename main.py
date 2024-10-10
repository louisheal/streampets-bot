import os
from threading import Thread
from pathlib import Path
import json

from flask import Flask, Response, stream_with_context, jsonify, request
from flask_cors import CORS
from werkzeug.serving import is_running_from_reloader
from dotenv import load_dotenv

from queues import JsonQueue
from chat_bots import ChatBot
from message_announcer import MessageAnnouncer
from utils import CHANNEL_NAME
from models import Color
from database import LibSqlDatabase


load_dotenv()

app = Flask(__name__)
CORS(app)

db_token = os.getenv('DB_TOKEN')
db_url = os.getenv('DB_URL')

announcer = MessageAnnouncer()
queue = JsonQueue(Path('data','queue.json'))

database = LibSqlDatabase(db_token, db_url)
bot = ChatBot(queue, database, announcer, os.getenv('BOT_TOKEN'), '!', [CHANNEL_NAME])

@app.route('/listen')
def listen():

  @stream_with_context
  def stream():
    messages = announcer.listen()
    while True:
      msg = messages.get()
      yield msg

  return Response(stream(), mimetype='text/event-stream')

@app.route('/viewers')
def viewers():
  rexs = bot.get_viewer_rexs()
  json_rexs = [rex.to_dict() for rex in rexs]
  return jsonify(json_rexs)

@app.route('/colors', methods=['GET'])
def get_colors():
  colors = [color.name.lower() for color in Color]
  return jsonify(colors)

@app.route('/colors', methods=['PUT'])
def update_color():
  data = request.get_json()
  color = Color.str_to_color(data['color'])
  trex = database.set_trex_color('ljrexcodes', color)
  announcer.announce(msg=json.dumps(trex.to_dict()), event='COLOR')
  return jsonify(success=True)

def run_bot():
  thread = Thread(target=bot.run, daemon=True)
  thread.start()
  print("Bot running...")

def create_app():
  if not is_running_from_reloader():
    run_bot()
  print("App running...")
  return app

if __name__ == '__main__':
  app = create_app()
  app.run(host="localhost")

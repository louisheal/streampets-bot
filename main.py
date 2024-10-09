import os
from threading import Thread

from flask import Flask, Response, stream_with_context, jsonify
from flask_cors import CORS
from werkzeug.serving import is_running_from_reloader
from dotenv import load_dotenv

from queues import JsonQueue
from bots import ChatBot
from message_announcer import MessageAnnouncer
from utils import CHANNEL_NAME
from trex import TRex


load_dotenv()

app = Flask(__name__)
CORS(app)

announcer = MessageAnnouncer()
queue = JsonQueue('queue.json')
bot = ChatBot(queue, os.getenv('BOT_TOKEN'), '!', [CHANNEL_NAME], announcer)


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
def viewers() -> list[TRex]:
  rexs = bot.get_viewer_rexs()
  return jsonify(rexs)


if __name__ == '__main__':
  
  if not is_running_from_reloader():
    thread = Thread(target=bot.run, daemon=True)
    thread.start()

  app.run(host="localhost")

import os
import json
from threading import Lock
from flask import Flask, request, abort, send_from_directory
from flask_socketio import SocketIO

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'secret!')
# Use eventlet if available for better websocket support
socketio = SocketIO(app, cors_allowed_origins='*')

ticker_lock = Lock()

PET_STATE = {
    'hunger': 50,
    'happiness': 50,
    'health': 50,
    'sleeping': False
}

DECAY_SECONDS = 60


def clamp(val, min_v=0, max_v=100):
    return max(min_v, min(max_v, val))


def decay():
    """Background decay loop."""
    with app.app_context():
        while True:
            socketio.sleep(DECAY_SECONDS)
            with ticker_lock:
                if PET_STATE['sleeping']:
                    continue
                PET_STATE['hunger'] = clamp(PET_STATE['hunger'] + 1)
                PET_STATE['happiness'] = clamp(PET_STATE['happiness'] - 1)
                if PET_STATE['hunger'] > 80:
                    PET_STATE['health'] = clamp(PET_STATE['health'] - 2)
                check_sleep()
            socketio.emit('pet_update', PET_STATE)


def check_sleep():
    if any(PET_STATE[key] <= 0 for key in ('hunger', 'happiness', 'health')):
        PET_STATE['sleeping'] = True
    else:
        PET_STATE['sleeping'] = False


@app.route('/')
def index():
    return send_from_directory('static', 'index.html')


def verify_eventsub(req):
    # Placeholder verification. In production, verify Twitch signature headers.
    return True


@app.route('/webhook/bits', methods=['POST'])
def webhook_bits():
    if not verify_eventsub(request):
        abort(403)
    data = request.json or {}
    bits = int(data.get('bits', 0))
    user = data.get('user', 'anon')
    with ticker_lock:
        if bits >= 100:
            # special treat
            PET_STATE['hunger'] = clamp(PET_STATE['hunger'] - 10)
            PET_STATE['happiness'] = clamp(PET_STATE['happiness'] + 10)
            PET_STATE['health'] = clamp(PET_STATE['health'] + 10)
            action = 'special_treat'
        elif bits >= 20:
            PET_STATE['happiness'] = clamp(PET_STATE['happiness'] + 20)
            PET_STATE['hunger'] = clamp(PET_STATE['hunger'] + 10)
            action = 'play'
        elif bits >= 10:
            PET_STATE['hunger'] = clamp(PET_STATE['hunger'] - 20)
            PET_STATE['happiness'] = clamp(PET_STATE['happiness'] + 5)
            action = 'feed'
        else:
            return '', 204
        check_sleep()
    socketio.emit('pet_update', PET_STATE)
    socketio.emit('action_performed', {'action': action, 'user': user})
    return '', 200


@app.route('/webhook/channel-point', methods=['POST'])
def webhook_channel_point():
    if not verify_eventsub(request):
        abort(403)
    data = request.json or {}
    with ticker_lock:
        PET_STATE['health'] = clamp(PET_STATE['health'] + 30)
        check_sleep()
    socketio.emit('pet_update', PET_STATE)
    socketio.emit('action_performed', {'action': 'heal', 'user': data.get('user', 'anon')})
    return '', 200


@socketio.on('connect')
def on_connect():
    socketio.emit('pet_update', PET_STATE)


if __name__ == '__main__':
    socketio.start_background_task(decay)
    socketio.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
    print("Server started on port", os.environ.get('PORT', 5000))
    print("Visit http://localhost:5000 to interact with the pet.")
    print("Press Ctrl+C to stop the server.")

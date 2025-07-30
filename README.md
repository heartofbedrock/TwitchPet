# TwitchPet

A simple Twitch-integrated virtual pet built with Flask, Flask-SocketIO and Phaser.

## Running locally

1. Install Python dependencies:
   ```bash
   pip install flask flask-socketio eventlet
   ```
2. Start the server:
   ```bash
   python app.py
   ```
3. Open `http://localhost:5000` in your browser.

## Twitch Webhooks

This prototype exposes `/webhook/bits` and `/webhook/channel-point` endpoints that mimic Twitch EventSub events. In production you must verify requests using the `Twitch-Eventsub-Message-Signature` header.

## Deployment Notes

Deploy the Flask app to any platform that offers HTTPS (Heroku, AWS). Ensure that the public URL is reachable by Twitch for webhooks.

To keep the decay loop running every 60 seconds, the server starts a background task when launched.

On Heroku:

1. Set `WEB_CONCURRENCY=1` and use the `eventlet` worker in `Procfile`:
   ```
   web: python app.py
   ```
2. Configure your domain with TLS (e.g. via Heroku SSL) and register webhook URLs in Twitch Developer Console.

## Files

- `app.py` – Flask backend with webhook routes and Socket.IO.
- `static/index.html` – Phaser game frontend.
- `static/js/game.js` – Phaser scene logic.
- `sprites/pet.png` – Placeholder sprite sheet with 4 frames.

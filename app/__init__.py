"""
Module: app

This module initializes the Flask application, sets up routes, database, and SocketIO events.

Dependencies:
    - Flask
    - flask_socketio
    - .routes
    - .database
    - .models
"""

from flask import Flask
from .routes import routes
from .database import init_db
from flask_socketio import SocketIO
from .models import websocket, handle_image

app = Flask(__name__)
app.config['SECRET_KEY'] = 'AEH'
socketio = SocketIO(app)

# Initialize routes
routes(app)
websocket(app)

# Initialize the database
init_db()

# Adding SocketIO event handler
socketio.on_event('image', handle_image)

if __name__ == '__main__':
    socketio.run(app, debug=True)

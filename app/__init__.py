from flask import Flask
from .routes import home, login_form, login, register, userprofile, get_user_data, purchase_plan, purchase_form
from .database import init_db
from flask_socketio import SocketIO
from .models import websocket_index, handle_image

app = Flask(__name__)
app.config['SECRET_KEY'] = 'AEH'
socketio = SocketIO(app)

# Adding URL rules for the initial routes
app.add_url_rule('/', view_func=home)
app.add_url_rule('/login', view_func=login_form, methods=['GET'])
app.add_url_rule('/login', view_func=login, methods=['POST'])
app.add_url_rule('/register', view_func=register, methods=['GET', 'POST'])
app.add_url_rule('/userprofile', view_func=userprofile, methods=['GET'])
app.add_url_rule('/get-user-data', view_func=get_user_data, methods=['GET'])
app.add_url_rule('/purchase_form', view_func=purchase_form, methods=['GET'])
app.add_url_rule('/purchase_plan', view_func=purchase_plan, methods=['POST'])
app.add_url_rule('/websocket', view_func=websocket_index)  # Adding websocket route

# Initialize the database
init_db()

# Adding SocketIO event handler
socketio.on_event('image', handle_image)

if __name__ == '__main__':
    socketio.run(app, debug=True)

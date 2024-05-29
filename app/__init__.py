from flask import Flask
from .routes import home, login, register, userprofile, get_user_data, purchase_plan, purchase_form, logout, interpreter, delete_account, reset_password, reset_with_token, reset_password_link, pricing, get_plan_price, get_plans, change_password
from .database import init_db
from flask_socketio import SocketIO
from .models import websocket_index, handle_image

app = Flask(__name__)
app.config['SECRET_KEY'] = 'AEH'
socketio = SocketIO(app)

# Adding URL rules for the initial routes
app.add_url_rule('/', view_func=home)
app.add_url_rule('/login', view_func=login, methods=['GET', 'POST'])
app.add_url_rule('/register', view_func=register, methods=['GET', 'POST'])
app.add_url_rule('/userprofile', view_func=userprofile, methods=['GET'])
app.add_url_rule('/get-user-data', view_func=get_user_data, methods=['GET'])
app.add_url_rule('/purchase_form', view_func=purchase_form, methods=['GET'])
app.add_url_rule('/purchase_plan', view_func=purchase_plan, methods=['POST'])
app.add_url_rule('/logout', view_func=logout, methods=['GET'])
app.add_url_rule('/sli', view_func=interpreter)
app.add_url_rule('/pricing', view_func=pricing)
app.add_url_rule('/websocket', view_func=websocket_index)
app.add_url_rule('/delete_account', view_func=delete_account, methods=['POST'])
app.add_url_rule('/reset_password', view_func=reset_password, methods=['POST'])
app.add_url_rule('/reset_password_link', view_func=reset_password_link, methods=['POST'])
app.add_url_rule('/reset/<token>', view_func=reset_with_token, methods=['GET', 'POST'])
app.add_url_rule('/get-plans', view_func=get_plans, methods=['GET'])
app.add_url_rule('/get-plan-price/<plan_name>', view_func=get_plan_price, methods=['GET'])
app.add_url_rule('/change_password', view_func=change_password, methods=['POST'])

# Initialize the database
init_db()

# Adding SocketIO event handler
socketio.on_event('image', handle_image)

if __name__ == '__main__':
    socketio.run(app, debug=True)

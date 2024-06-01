from flask import Flask
from .routes import Authentication, PasswordManagement, PaymentManagement, PlansManagement, UserDataManagement
from .database import DatabaseConnection, DatabaseInitializer, UserPrivilegesManager, UserResetManager
from flask_socketio import SocketIO
from .models import websocket_index, handle_image

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'AEH'

# Initialize database
DatabaseInitializer.init_db()

# Initialize SocketIO
socketio = SocketIO(app)

# URL routes
app.add_url_rule('/', view_func=Authentication.home)
app.add_url_rule('/interpreter', view_func=Authentication.interpreter)
app.add_url_rule('/login', view_func=Authentication.login, methods=['GET', 'POST'])
app.add_url_rule('/register', view_func=Authentication.register, methods=['GET', 'POST'])
app.add_url_rule('/userprofile', view_func=Authentication.user_profile)
app.add_url_rule('/logout', view_func=Authentication.logout)
app.add_url_rule('/get-user-data', view_func=UserDataManagement.get_user_data)
app.add_url_rule('/purchase_form', view_func=PaymentManagement.purchase_form, methods=['GET'])
app.add_url_rule('/purchase_plan', view_func=PaymentManagement.purchase_plan, methods=['POST'])
app.add_url_rule('/delete_account', view_func=UserDataManagement.delete_account, methods=['POST'])
app.add_url_rule('/reset_password', view_func=PasswordManagement.reset_password, methods=['POST'])
app.add_url_rule('/reset_password_link', view_func=PasswordManagement.reset_password_link)
app.add_url_rule('/reset/<token>', view_func=PasswordManagement.reset_with_token, methods=['GET', 'POST'])
app.add_url_rule('/pricing', view_func=PlansManagement.pricing)
app.add_url_rule('/get-plans', view_func=PlansManagement.get_plans)
app.add_url_rule('/get-plan-price/<plan_name>', view_func=PlansManagement.get_plan_price, methods=['GET'])
app.add_url_rule('/generate_reset_token', view_func=PasswordManagement.generate_reset_token, methods=['GET', 'POST'])

# WebSocket route
app.add_url_rule('/websocket', view_func=websocket_index)

# SocketIO event handler
@socketio.on('image')
def handle_image(image):
    handle_image(image)

if __name__ == '__main__':
    socketio.run(app, debug=True)

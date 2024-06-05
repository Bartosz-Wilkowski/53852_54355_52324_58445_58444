import mysql.connector
from mysql.connector import Error
from datetime import datetime
import pytest
from flask import Flask, render_template, session
from flask_socketio import SocketIO, emit
from tensorflow.keras.models import load_model
import numpy as np
import cv2
import base64
import mediapipe as mp
import uuid
from flask_socketio import SocketIOTestClient

# Database functions

def create_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='AEHprojekt'
        )
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("CREATE DATABASE IF NOT EXISTS user_auth")
            cursor.close()
            connection.close()

        connection = mysql.connector.connect(
            host='localhost',
            database='user_auth',
            user='root',
            password='AEHprojekt'
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error: {e}")
    return None

def init_db():
    connection = create_connection()
    if connection is None:
        print("Failed to connect to the database.")
        return
    cursor = connection.cursor()

    # Create subscription_plan table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscription_plan (
            plan_id INT AUTO_INCREMENT PRIMARY KEY,
            plan_name VARCHAR(255) NOT NULL,
            daily_limit INT,
            price DOUBLE,
            UNIQUE (plan_name)   
        )
    ''')

    # Insert three plans into subscription_plan table using INSERT IGNORE
    cursor.execute('''
        INSERT IGNORE INTO subscription_plan (plan_name, daily_limit, price) VALUES
        ('Basic', 25, 0),
        ('Standard', 250, 19.99),
        ('Unlimited', 0, 49.99)
    ''')

    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            password VARCHAR(255) NOT NULL,
            name VARCHAR(255),
            surname VARCHAR(255),
            plan_name VARCHAR(255),
            recognized_count INT,       
            last_reset datetime,
            UNIQUE (username),
            UNIQUE (email),
            reset_token VARCHAR(255),
            FOREIGN KEY (plan_name) REFERENCES subscription_plan(plan_name)
        )
    ''')

    # Insert aehuser user into users table using INSERT IGNORE
    cursor.execute('''
        INSERT IGNORE INTO users (username, email, password, name, surname, plan_name) VALUES
        ('aehuser', 'aehuser@aeh.pl', 'Aehuser1', 'Aeh', 'User', 'Unlimited')
    ''')

    # Create payments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            payment_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            payment_date date,
            amount double,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    connection.commit()
    cursor.close()
    connection.close()

def revoke_drop_privileges():
    connection = create_connection()
    if connection is None:
        print("Failed to connect to the database.")
        return
    cursor = connection.cursor()

    try:
        cursor.execute('''
            SELECT GROUP_CONCAT(CONCAT('REVOKE DROP ON `user_auth`.* FROM `', user, '`@`', host, '`;') SEPARATOR ' ')
            INTO @sql
            FROM mysql.db
            WHERE db = 'user_auth' AND user != 'root' AND user != 'mysql.sys';
        ''')

        cursor.execute("SET @sql = IFNULL(@sql, '');")
        cursor.execute('PREPARE stmt FROM @sql;')
        cursor.execute('EXECUTE stmt;')
        cursor.execute('DEALLOCATE PREPARE stmt;')
        print("DROP privileges revoked successfully.")
    except Error as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        connection.close()

def reset_recognized_count():
    connection = create_connection()
    if connection is None:
        print("Failed to connect to the database.")
        return
    cursor = connection.cursor()

    try:
        now = datetime.now()
        midnight = datetime.combine(now.date(), datetime.min.time())
        
        cursor.execute('''
            UPDATE users
            SET recognized_count = 0, last_reset = %s
            WHERE plan_name IN ('Basic', 'Standard') AND (last_reset IS NULL OR last_reset < %s)
        ''', (midnight, midnight))
        
        connection.commit()
        print("recognized_count reset and last_reset updated successfully for Basic and Standard plans.")
    except Error as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        connection.close()

# Flask application

app = Flask(__name__)
app.config['SECRET_KEY'] = 'AEH'
socketio = SocketIO(app)
model = load_model('models/final_model/final_model.h5')

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands.Hands(
    static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Labels for the gesture recognition model
labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O',
          'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'del', 'nothing', 'space']

def websocket_index():
    return render_template('index.html')

def get_user_sign_limit():
    if 'username' in session:
        username = session['username']
    else:
        if 'guest_id' not in session:
            session['guest_id'] = str(uuid.uuid4())
        username = session['guest_id']
    
    connection = create_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute('''
            SELECT users.plan_name, users.last_reset, users.recognized_count, subscription_plan.daily_limit
            FROM users
            JOIN subscription_plan ON users.plan_name = subscription_plan.plan_name
            WHERE users.username = %s
        ''', (username,))
        user_data = cursor.fetchone()
        cursor.close()
        connection.close()
        if user_data:
            last_reset = user_data['last_reset']
            daily_limit = user_data['daily_limit']
            if last_reset is None or (datetime.now() - last_reset).days >= 1:
                reset_recognition_count(username)
                last_reset = datetime.now()
                update_last_reset(username, last_reset)
            return daily_limit if daily_limit is not None else float('inf')
    return 10

def reset_recognition_count(username):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE users SET recognized_count = 0 WHERE username = %s", (username,))
        connection.commit()
        cursor.close()
        connection.close()

def update_last_reset(username, last_reset):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE users SET last_reset = %s WHERE username = %s", (last_reset, username))
        connection.commit()
        cursor.close()
        connection.close()

def update_recognized_count(username, count):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE users SET recognized_count = %s WHERE username = %s", (count, username))
        connection.commit()
        cursor.close()
        connection.close()

@socketio.on('image')
def handle_image(data):
    if 'recognized_count' not in session:
        session['recognized_count'] = 0

    limit = get_user_sign_limit()
    if session['recognized_count'] >= limit:
        emit('limit_reached')
        return

    img_data = base64.b64decode(data['image'])
    np_img = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Process the image using MediaPipe Hands
    results = mp_hands.process(img)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
        
            h, w, _ = img.shape
            x_min = int(min(lm.x for lm in hand_landmarks.landmark) * w)
            x_max = int(max(lm.x for lm in hand_landmarks.landmark) * w)                 
            y_min = int(min(lm.y for lm in hand_landmarks.landmark) * h)
            y_max = int(max(lm.y for lm in hand_landmarks.landmark) * h)

            x_min = max(0, x_min)
            y_min = max(0, y_min)
            x_max = min(w, x_max)
            y_max = min(h, y_max)

            roi = img[y_min:y_max, x_min:x_max]
            if roi.size == 0:
                continue
            zoomed_roi = cv2.resize(roi, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_LINEAR)

            new_y_max = min(y_min + zoomed_roi.shape[0], h)
            new_y_min = max(0, new_y_max - zoomed_roi.shape[0])
            new_x_max = min(x_min + zoomed_roi.shape[1], w)
            new_x_min = max(0, new_x_max - zoomed_roi.shape[1])

            zoomed_roi = zoomed_roi[:new_y_max-new_y_min, :new_x_max-new_x_min]

            img[new_y_min:new_y_max, new_x_min:new_x_max] = zoomed_roi

            landmarks = []
            for lm in hand_landmarks.landmark:
                landmarks.append([lm.x, lm.y, lm.z])

            landmarks = np.array(landmarks).flatten()
            landmarks = (landmarks - np.min(landmarks)) / (np.max(landmarks) - np.min(landmarks))
            landmarks = np.expand_dims(landmarks, axis=0)

            prediction = model.predict(landmarks)
            predicted_class = labels[np.argmax(prediction)]

            session['recognized_count'] += 1

            if 'username' in session:
                username = session['username']
            else:
                username = session['guest_id']
            update_recognized_count(username, session['recognized_count'])

            emit('prediction', {'prediction': predicted_class})
            return

    emit('prediction', {'prediction': 'No hand detected'})

# Tests

@pytest.fixture
def client():
    flask_app = app
    socketio_test_client = SocketIOTestClient(flask_app, socketio)
    yield socketio_test_client

def test_create_connection():
    connection = create_connection()
    assert connection is not None
    assert connection.is_connected()
    connection.close()

def test_init_db():
    init_db()
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SHOW TABLES LIKE 'subscription_plan'")
    result = cursor.fetchone()
    assert result is not None
    cursor.execute("SHOW TABLES LIKE 'users'")
    result = cursor.fetchone()
    assert result is not None
    cursor.execute("SHOW TABLES LIKE 'payments'")
    result = cursor.fetchone()
    assert result is not None
    cursor.close()
    connection.close()

def test_reset_recognized_count():
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("UPDATE users SET recognized_count = 10 WHERE plan_name IN ('Basic', 'Standard')")
    connection.commit()
    reset_recognized_count()
    cursor.execute("SELECT recognized_count FROM users WHERE plan_name IN ('Basic', 'Standard')")
    result = cursor.fetchall()
    for row in result:
        assert row[0] == 0
    cursor.close()
    connection.close()

def test_revoke_drop_privileges():
    revoke_drop_privileges()
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SHOW GRANTS FOR 'root'@'localhost'")
    grants = cursor.fetchall()
    for grant in grants:
        assert 'DROP' not in grant[0]
    cursor.close()
    connection.close()

def test_handle_image(client):
    client.connect()
    with client.session_transaction() as sess:
        sess['recognized_count'] = 0
        sess['username'] = 'testuser'

    img = cv2.imread('path_to_sample_image.jpg')
    _, buffer = cv2.imencode('.jpg', img)
    img_str = base64.b64encode(buffer).decode()

    client.emit('image', {'image': img_str})
    received = client.get_received()

    assert received[0]['name'] == 'prediction'
    assert 'prediction' in received[0]['args'][0]

    client.disconnect()

if __name__ == "__main__":
    init_db()
    revoke_drop_privileges()
    reset_recognized_count()
    pytest.main(["-v"])

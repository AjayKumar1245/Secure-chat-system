from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from cryptography.fernet import Fernet
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Generate or load key
key_file = "secret.key"
if os.path.exists(key_file):
    with open(key_file, 'rb') as file:
        key = file.read()
else:
    key = Fernet.generate_key()
    with open(key_file, 'wb') as file:
        file.write(key)

cipher = Fernet(key)

@app.route('/')
def index():
    return render_template('index.html', messages=[])

@app.route('/get_encrypted')
def get_encrypted():
    msg = request.args.get('msg', '')
    encrypted_msg = cipher.encrypt(msg.encode()).decode()
    return encrypted_msg

@socketio.on('send_message')
def handle_send_message(data):
    message = data['message']
    emit('receive_message', {'message': message}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)

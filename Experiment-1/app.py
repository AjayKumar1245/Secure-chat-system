from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from cryptography.fernet import Fernet
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Load or generate Fernet key
if not os.path.exists("secret.key"):
    key = Fernet.generate_key()
    with open("secret.key", "wb") as f:
        f.write(key)
else:
    with open("secret.key", "rb") as f:
        key = f.read()

cipher = Fernet(key)
messages = []

@app.route('/')
def index():
    decrypted = [cipher.decrypt(m).decode() for m in messages]
    return render_template("index.html", messages=decrypted)

@app.route('/get_encrypted')
def get_encrypted():
    msg = request.args.get('msg', '')
    encrypted = cipher.encrypt(msg.encode())
    return encrypted.decode()

@socketio.on('send_message')
def handle_send(data):
    message = data['message']
    encrypted = cipher.encrypt(message.encode())
    messages.append(encrypted)
    decrypted = cipher.decrypt(encrypted).decode()
    print(f"🔐 Encrypted: {encrypted}\n💬 Decrypted: {decrypted}")
    emit('receive_message', {'message': decrypted}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)

from flask import Flask, render_template
from flask_socketio import SocketIO
import socket
import json
import threading
from collections import deque

app = Flask(__name__)
socketio = SocketIO(app)

# Set up TCP server configuration
server_ip = '0.0.0.0'
port = 56204

# Initialize a deque with a fixed maximum length
data_buffer = deque(maxlen=1000)

def start_tcp_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((server_ip, port))
        s.listen()
        print("TCP Server listening on port", port)
        
        while True:
            conn, addr = s.accept()
            print(f"Connected by {addr}")
            data_str = ""
            
            while True:
                data = conn.recv(1024).decode()
                if not data:
                    break
                
                data_str += data
                while '{' in data_str and '}' in data_str:
                    start = data_str.find('{')
                    end = data_str.find('}', start) + 1
                    json_str = data_str[start:end]
                    data_str = data_str[end:]
                    
                    try:
                        json_data = json.loads(json_str)
                        # Store the received data in the deque
                        data_buffer.append(json_data)
                        
                        # Emit the latest data to the frontend
                        socketio.emit('new_data', json_data)
                    except json.JSONDecodeError:
                        continue

@app.route('/')
def index():
    return render_template('index.html')

# Endpoint to fetch all current data in the deque for initial load
@socketio.on('fetch_all_data')
def handle_fetch_all_data():
    # Convert the deque to a list and send to frontend
    socketio.emit('all_data', list(data_buffer))

if __name__ == '__main__':
    # Start TCP server in a separate thread
    tcp_thread = threading.Thread(target=start_tcp_server)
    tcp_thread.daemon = True
    tcp_thread.start()
    
    # Run the Flask app with SocketIO
    socketio.run(app, host='0.0.0.0', port=5000)

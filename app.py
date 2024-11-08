# app.py
from flask import Flask, render_template
from flask_socketio import SocketIO
import socket
import json
import threading

app = Flask(__name__)
socketio = SocketIO(app)

# Set up TCP server configuration
server_ip = '0.0.0.0'
port = 56204

def start_tcp_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((server_ip, port))
        s.listen()
        print("TCP Server listening on port", port)
        
        while True:
            conn, addr = s.accept()
            print(f"Connected by {addr}")
            data_buffer = ""
            
            while True:
                data = conn.recv(1024).decode()
                if not data:
                    break
                
                data_buffer += data
                while '{' in data_buffer and '}' in data_buffer:
                    start = data_buffer.find('{')
                    end = data_buffer.find('}', start) + 1
                    json_str = data_buffer[start:end]
                    data_buffer = data_buffer[end:]
                    
                    try:
                        json_data = json.loads(json_str)
                        # print("Received data:", json_data)  # Print to console
                        socketio.emit('new_data', json_data)  # Send data to frontend
                    except json.JSONDecodeError:
                        continue

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    # Start TCP server in a separate thread
    tcp_thread = threading.Thread(target=start_tcp_server)
    tcp_thread.daemon = True
    tcp_thread.start()
    
    # Run the Flask app with SocketIO
    socketio.run(app, host='0.0.0.0', port=5000)

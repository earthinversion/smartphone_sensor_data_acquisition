import socket
import json
import sqlite3
from datetime import datetime

def run_tcp_server():
    server_ip = '0.0.0.0'  # Listens on all interfaces
    port = 56204

    # Connect to SQLite database (creates if it doesn't exist)
    conn = sqlite3.connect('sensor_data.db', check_same_thread=False)
    cursor = conn.cursor()

    # Create the table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS accelerometer_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            loggingTime TEXT,
            accelerometerAccelerationX REAL,
            accelerometerAccelerationY REAL,
            accelerometerAccelerationZ REAL
        )
    ''')
    conn.commit()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((server_ip, port))
        s.listen()
        print("TCP Server listening on port", port)

        while True:
            try:
                conn_socket, addr = s.accept()
                print(f"Connected by {addr}")
                data_buffer_str = ""  # Buffer to accumulate incoming data

                while True:
                    data = conn_socket.recv(1024).decode()
                    if not data:
                        break

                    data_buffer_str += data
                    while '{' in data_buffer_str and '}' in data_buffer_str:
                        start = data_buffer_str.find('{')
                        end = data_buffer_str.find('}', start) + 1
                        json_str = data_buffer_str[start:end]
                        data_buffer_str = data_buffer_str[end:]

                        try:
                            json_data = json.loads(json_str)
                            # Extract the required fields
                            loggingTime = json_data.get('loggingTime', datetime.now().isoformat())
                            accX = json_data.get('accelerometerAccelerationX', 0.0)
                            accY = json_data.get('accelerometerAccelerationY', 0.0)
                            accZ = json_data.get('accelerometerAccelerationZ', 0.0)

                            # Insert data into SQLite database
                            cursor.execute('''
                                INSERT INTO accelerometer_data (loggingTime, accelerometerAccelerationX, accelerometerAccelerationY, accelerometerAccelerationZ)
                                VALUES (?, ?, ?, ?)
                            ''', (loggingTime, accX, accY, accZ))
                            conn.commit()

                            # print(f"Data inserted: {loggingTime}, {accX}, {accY}, {accZ}")

                        except json.JSONDecodeError as e:
                            print(f"JSON Decode Error: {e}")
                            continue
                conn_socket.close()
            except Exception as e:
                print(f"Connection error: {e}")

if __name__ == "__main__":
    run_tcp_server()
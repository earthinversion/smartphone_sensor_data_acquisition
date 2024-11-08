import socket
import json
import pandas as pd
import os

server_ip = '0.0.0.0'  # Listens on all interfaces
port = 56204
data_file = "data.csv"

# Initialize the CSV file with headers if it doesn't exist
if not os.path.isfile(data_file):
    pd.DataFrame().to_csv(data_file, index=False)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((server_ip, port))
    s.listen()
    print("TCP Server listening on port", port)

    while True:
        try:
            conn, addr = s.accept()
            print(f"Connected by {addr}")
            data_buffer = ""  # Buffer to accumulate incoming data

            while True:
                data = conn.recv(1024).decode()  # Decode received bytes
                if not data:
                    break

                data_buffer += data  # Append chunk to buffer

                # Process complete JSON objects within the buffer
                while '{' in data_buffer and '}' in data_buffer:
                    # Extract JSON object from buffer
                    start = data_buffer.find('{')
                    end = data_buffer.find('}', start) + 1
                    json_str = data_buffer[start:end]
                    data_buffer = data_buffer[end:]  # Remove processed part

                    # Parse JSON and write to CSV
                    try:
                        json_data = json.loads(json_str)  # Convert JSON string to dict
                        df = pd.DataFrame([json_data])  # Convert to DataFrame

                        # Append to CSV file
                        df.to_csv(data_file, mode='a', header=not os.path.isfile(data_file), index=False)
                    
                    except json.JSONDecodeError as e:
                        print(f"JSON Decode Error: {e}")
                        continue  # If JSON is incomplete, wait for more data

        except Exception as e:
            print(f"Connection error: {e}")

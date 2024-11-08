import socket
import json
import threading
from collections import deque
import streamlit as st
import pandas as pd
import time

# Initialize a deque to store incoming data
data_buffer = deque(maxlen=1000)  # Adjust maxlen as needed

def run_tcp_server():
    server_ip = '0.0.0.0'  # Listens on all interfaces
    port = 56204

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((server_ip, port))
        s.listen()
        print("TCP Server listening on port", port)

        while True:
            try:
                conn, addr = s.accept()
                print(f"Connected by {addr}")
                data_buffer_str = ""  # Buffer to accumulate incoming data

                while True:
                    data = conn.recv(1024).decode()
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
                            data_buffer.append(json_data)
                        except json.JSONDecodeError as e:
                            print(f"JSON Decode Error: {e}")
                            continue
                        # print(json_data)
                        print(f"Data buffer size: {len(data_buffer)}")
            except Exception as e:
                print(f"Connection error: {e}")

@st.cache_resource
def get_tcp_server_thread():
    tcp_thread = threading.Thread(target=run_tcp_server, daemon=True)
    tcp_thread.start()
    return tcp_thread

# Start the TCP server (only once)
get_tcp_server_thread()

st.title("Real-Time Accelerometer Data Visualization")

# Initialize an empty DataFrame to store the data
if 'data_df' not in st.session_state:
    st.session_state['data_df'] = pd.DataFrame()

# Placeholder for the chart
chart_placeholder = st.empty()

# Check if there is new data in the buffer
if len(data_buffer) > 0:
    # print(f"Received {len(data_buffer)} new data points")
    # Transfer data from the deque to a list
    data_list = []
    while len(data_buffer) > 0:
        data_list.append(data_buffer.popleft())

    # Convert the list of dictionaries to a DataFrame
    new_data_df = pd.DataFrame(data_list)

    # print(new_data_df.head())

    # Append the new data to the existing DataFrame
    st.session_state['data_df'] = pd.concat([st.session_state['data_df'], new_data_df], ignore_index=True)

    # Keep only the latest N data points
    st.session_state['data_df'] = st.session_state['data_df'].tail(1000)

# Proceed if there's data to display
if not st.session_state['data_df'].empty:
    # Ensure 'loggingTime' is in datetime format
    if 'loggingTime' in st.session_state['data_df'].columns:
        st.session_state['data_df']['Time'] = pd.to_datetime(st.session_state['data_df']['loggingTime'])
    else:
        st.session_state['data_df']['Time'] = pd.to_datetime(st.session_state['data_df']['timestamp'], unit='s')

    # Prepare data for plotting
    chart_data = st.session_state['data_df'][['Time', 'accelerometerAccelerationX', 'accelerometerAccelerationY', 'accelerometerAccelerationZ']].set_index('Time')

    # Plot the data
    chart_placeholder.line_chart(chart_data)

# Add a refresh mechanism
time.sleep(1)
st.rerun()

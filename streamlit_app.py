import streamlit as st
import pandas as pd
import sqlite3
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time

# st.title("Real-Time Accelerometer Data Visualization")

# Connect to SQLite database
conn = sqlite3.connect('sensor_data.db', check_same_thread=False)


total_data_points = 1000

# Initialize session state variables
if 'data_df' not in st.session_state:
    st.session_state['data_df'] = pd.DataFrame()

if 'last_timestamp' not in st.session_state:
    st.session_state['last_timestamp'] = None

# Create a placeholder for the chart
chart_placeholder = st.empty()

# Function to fetch new data
def fetch_new_data():
    if st.session_state['last_timestamp'] is None:
        query = '''
            SELECT loggingTime, accelerometerAccelerationX, accelerometerAccelerationY, accelerometerAccelerationZ
            FROM accelerometer_data
            ORDER BY loggingTime ASC
        '''
        data_df = pd.read_sql_query(query, conn)
    else:
        query = '''
            SELECT loggingTime, accelerometerAccelerationX, accelerometerAccelerationY, accelerometerAccelerationZ
            FROM accelerometer_data
            WHERE loggingTime > ?
            ORDER BY loggingTime ASC
        '''
        data_df = pd.read_sql_query(query, conn, params=(st.session_state['last_timestamp'],))
    return data_df

# Initialize the figure
fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                    vertical_spacing=0.02,
                    # subplot_titles=("Acceleration X", "Acceleration Y", "Acceleration Z")
                    )

# Main loop to update the chart
while True:
    new_data = fetch_new_data()
    if not new_data.empty:
        # Ensure 'loggingTime' is in datetime format
        new_data['Time'] = pd.to_datetime(new_data['loggingTime'])

        # Update last_timestamp
        st.session_state['last_timestamp'] = new_data['loggingTime'].max()

        # Append new data to the existing DataFrame
        st.session_state['data_df'] = pd.concat(
            [st.session_state['data_df'], new_data], ignore_index=True
        )

        # Keep only the latest N data points
        st.session_state['data_df'] = st.session_state['data_df'].tail(total_data_points)

        time_series = st.session_state['data_df']['Time']

        # Clear existing traces
        fig.data = []

        # Acceleration X
        fig.add_trace(go.Scatter(
            x=time_series,
            y=st.session_state['data_df']['accelerometerAccelerationX'],
            mode='lines',
            name='Acceleration X'),
            row=1, col=1)

        # Acceleration Y
        fig.add_trace(go.Scatter(
            x=time_series,
            y=st.session_state['data_df']['accelerometerAccelerationY'],
            mode='lines',
            name='Acceleration Y'),
            row=2, col=1)

        # Acceleration Z
        fig.add_trace(go.Scatter(
            x=time_series,
            y=st.session_state['data_df']['accelerometerAccelerationZ'],
            mode='lines',
            name='Acceleration Z'),
            row=3, col=1)

        # Update layout
        fig.update_layout(height=600, showlegend=False)

        # Update x-axis label
        fig.update_xaxes(title_text="Time", row=3, col=1)

        # Update y-axis labels
        fig.update_yaxes(title_text="Acceleration X", row=1, col=1)
        fig.update_yaxes(title_text="Acceleration Y", row=2, col=1)
        fig.update_yaxes(title_text="Acceleration Z", row=3, col=1)

        # Display the updated figure
        chart_placeholder.plotly_chart(fig, use_container_width=True)
    else:
        if st.session_state['data_df'].empty:
            st.write("Waiting for data...")

    # Wait for a short period before updating again
    time.sleep(0.1)

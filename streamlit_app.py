import streamlit as st
import pandas as pd
import sqlite3
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import asyncio

st.title("Real-Time Accelerometer Data Visualization")

# Connect to SQLite database
conn = sqlite3.connect('sensor_data.db', check_same_thread=False)

total_data_points = 2000

# Initialize session state variables
if 'data_df' not in st.session_state:
    st.session_state['data_df'] = pd.DataFrame()

if 'last_timestamp' not in st.session_state:
    st.session_state['last_timestamp'] = None

# Create a placeholder for the chart
chart_placeholder = st.empty()

# Initialize the figure without subplot titles
fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                    vertical_spacing=0.02)

# Initialize empty traces
trace_x = go.Scatter(x=[], y=[], mode='lines', name='Acceleration X')
trace_y = go.Scatter(x=[], y=[], mode='lines', name='Acceleration Y')
trace_z = go.Scatter(x=[], y=[], mode='lines', name='Acceleration Z')

fig.add_trace(trace_x, row=1, col=1)
fig.add_trace(trace_y, row=2, col=1)
fig.add_trace(trace_z, row=3, col=1)

# Update layout
fig.update_layout(height=800, showlegend=False)

# Update x-axis label
fig.update_xaxes(title_text="Time", row=3, col=1)

# Update y-axis labels
fig.update_yaxes(title_text="Acceleration X", row=1, col=1)
fig.update_yaxes(title_text="Acceleration Y", row=2, col=1)
fig.update_yaxes(title_text="Acceleration Z", row=3, col=1)

# Display the figure
chart = chart_placeholder.plotly_chart(fig, use_container_width=True)

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

# Asynchronous function to update the chart
async def update_chart():
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

            # Update traces with new data
            with chart_placeholder.container():
                fig.update_traces(
                    selector=dict(name='Acceleration X'),
                    x=time_series,
                    y=st.session_state['data_df']['accelerometerAccelerationX']
                )
                fig.update_traces(
                    selector=dict(name='Acceleration Y'),
                    x=time_series,
                    y=st.session_state['data_df']['accelerometerAccelerationY']
                )
                fig.update_traces(
                    selector=dict(name='Acceleration Z'),
                    x=time_series,
                    y=st.session_state['data_df']['accelerometerAccelerationZ']
                )

                # Update the chart
                chart_placeholder.plotly_chart(fig, use_container_width=True)
        else:
            if st.session_state['data_df'].empty:
                st.write("Waiting for data...")

        # Wait for a short period before updating again
        await asyncio.sleep(1)

# Run the asynchronous update function
asyncio.run(update_chart())

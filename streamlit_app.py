import streamlit as st
import pandas as pd
import sqlite3
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time

# Connect to SQLite database
conn = sqlite3.connect('sensor_data.db', check_same_thread=False)

data_length_to_display = 60  # seconds
sampling_rate = 50  # Hz
total_data_points = data_length_to_display * sampling_rate

# Initialize session state variables
if 'data_df' not in st.session_state:
    st.session_state['data_df'] = pd.DataFrame()

if 'last_timestamp' not in st.session_state:
    st.session_state['last_timestamp'] = None

# Create placeholders for the chart and battery level
# col1, col2 = st.columns(2)
# battery_placeholder = col1.empty()
# location_placeholder = col2.empty()
chart_placeholder = st.empty()
battery_placeholder = st.empty()
location_placeholder = st.empty()

# Function to fetch new accelerometer data
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

# Function to fetch the latest battery level
def fetch_battery_level():
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute('SELECT batteryLevel, loggingTime FROM accelerometer_data ORDER BY loggingTime DESC LIMIT 1')
            result = cursor.fetchone()
            # print(result)
            return result if result else None
    except sqlite3.OperationalError as e:
        st.write(f"SQLite Error: {e}")
        return None

# Function to fetch the latest location
def fetch_location():
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute('SELECT locationLatitude, locationLongitude FROM accelerometer_data ORDER BY loggingTime DESC LIMIT 1')
            result = cursor.fetchone()
            return result if result else None
    except sqlite3.OperationalError as e:
        st.write(f"SQLite Error: {e}")
        return None

# Initialize the figure
device_id = 'Unknown'
identifierForVendor = 'Unknown'
try:
    with conn:
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT deviceID FROM accelerometer_data')
        device_id = cursor.fetchone()[0]
        cursor.execute('SELECT DISTINCT identifierForVendor FROM accelerometer_data')
        identifierForVendor = cursor.fetchone()[0]
except sqlite3.OperationalError as e:
    st.write(f"SQLite Error: {e}")

fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                    vertical_spacing=0.02,
                    subplot_titles=(f"{device_id} ({identifierForVendor})", "", "")
                    )

# Main loop to update the chart and battery level
## battery level update every 10 seconds but data update every 1 second

## first fetch of the battery level
time_counter = 0
battery_level, battery_level_logtime = fetch_battery_level()
if battery_level is not None:
    battery_placeholder.metric("Battery Level", f"{battery_level*100:.1f}% ({battery_level_logtime})")

locationLatitude, locationLongitude = fetch_location()
if locationLatitude is not None and locationLongitude is not None:
    location_df = pd.DataFrame({'lat': [locationLatitude], 'lon': [locationLongitude]})
    location_placeholder.map(location_df, size=5, zoom=14)


## run the main loop to update the chart and battery level every xx second
while True:
    # Fetch and display the battery level
    if time_counter>=10:
        time_counter = 0
        battery_level, battery_level_logtime = fetch_battery_level()
        if battery_level is not None:
            battery_placeholder.metric("Battery Level", f"{battery_level*100:.1f}% ({battery_level_logtime})")

        locationLatitude, locationLongitude = fetch_location()
        if locationLatitude is not None and locationLongitude is not None:
            location_df = pd.DataFrame({'lat': [locationLatitude], 'lon': [locationLongitude]})
            location_placeholder.map(location_df, size=5, zoom=14)

    time_counter += 1
    new_data = fetch_new_data()
    if not new_data.empty:
        new_data['Time'] = pd.to_datetime(new_data['loggingTime'])
        st.session_state['last_timestamp'] = new_data['loggingTime'].max()
        st.session_state['data_df'] = pd.concat(
            [st.session_state['data_df'], new_data], ignore_index=True
        )
        st.session_state['data_df'] = st.session_state['data_df'].tail(total_data_points)

        time_series = st.session_state['data_df']['Time']
        fig.data = []

        fig.add_trace(go.Scatter(x=time_series, y=st.session_state['data_df']['accelerometerAccelerationX'], mode='lines', name='Acceleration X'), row=1, col=1)
        fig.add_trace(go.Scatter(x=time_series, y=st.session_state['data_df']['accelerometerAccelerationY'], mode='lines', name='Acceleration Y'), row=2, col=1)
        fig.add_trace(go.Scatter(x=time_series, y=st.session_state['data_df']['accelerometerAccelerationZ'], mode='lines', name='Acceleration Z'), row=3, col=1)

        fig.update_layout(height=600, showlegend=False)
        fig.update_xaxes(row=3, col=1)
        fig.update_yaxes(title_text="X", row=1, col=1)
        fig.update_yaxes(title_text="Y", row=2, col=1)
        fig.update_yaxes(title_text="Z", row=3, col=1)

        chart_placeholder.plotly_chart(fig, use_container_width=True)
    else:
        if st.session_state['data_df'].empty:
            st.write("Waiting for data...")

    # Wait for the next update
    time.sleep(1)

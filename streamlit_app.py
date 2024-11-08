import streamlit as st
import pandas as pd
import sqlite3
from streamlit_autorefresh import st_autorefresh

st.title("Real-Time Accelerometer Data Visualization")

# Connect to SQLite database
conn = sqlite3.connect('sensor_data.db', check_same_thread=False)
cursor = conn.cursor()

# Placeholder for the chart
chart_placeholder = st.empty()

# Function to read data from the database
def load_data():
    query = '''
        SELECT loggingTime, accelerometerAccelerationX, accelerometerAccelerationY, accelerometerAccelerationZ
        FROM accelerometer_data
        ORDER BY id DESC
        LIMIT 1000
    '''
    data_df = pd.read_sql_query(query, conn)
    data_df = data_df.sort_values('loggingTime')  # Sort by time ascending
    return data_df

# Read data
data_df = load_data()

if not data_df.empty:
    # Ensure 'loggingTime' is in datetime format
    try:
        data_df['Time'] = pd.to_datetime(data_df['loggingTime'])
    except Exception as e:
        st.error(f"Time conversion error: {e}")

    # Prepare data for plotting
    chart_data = data_df[['Time', 'accelerometerAccelerationX', 'accelerometerAccelerationY', 'accelerometerAccelerationZ']].set_index('Time')

    # Plot the data
    chart_placeholder.line_chart(chart_data)
else:
    st.write("Waiting for data...")

# Add a refresh mechanism
# Refresh the app every 1 second
st_autorefresh(interval=1000, key="data_refresh")

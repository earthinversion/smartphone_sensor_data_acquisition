import streamlit as st
import pandas as pd
import sqlite3
from streamlit_autorefresh import st_autorefresh
import plotly.graph_objs as go
from plotly.subplots import make_subplots

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
    time_series = data_df['Time']

    # Create subplots
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                        vertical_spacing=0.02,
                        subplot_titles=("Acceleration X", "Acceleration Y", "Acceleration Z"))

    # Acceleration X
    fig.add_trace(go.Scatter(x=time_series, y=data_df['accelerometerAccelerationX'],
                             mode='lines', name='Acceleration X'),
                  row=1, col=1)

    # Acceleration Y
    fig.add_trace(go.Scatter(x=time_series, y=data_df['accelerometerAccelerationY'],
                             mode='lines', name='Acceleration Y'),
                  row=2, col=1)

    # Acceleration Z
    fig.add_trace(go.Scatter(x=time_series, y=data_df['accelerometerAccelerationZ'],
                             mode='lines', name='Acceleration Z'),
                  row=3, col=1)

    # Update layout
    fig.update_layout(height=800, showlegend=False)

    # Update x-axis label
    fig.update_xaxes(title_text="Time", row=3, col=1)

    # Update y-axis labels
    fig.update_yaxes(title_text="Acceleration X", row=1, col=1)
    fig.update_yaxes(title_text="Acceleration Y", row=2, col=1)
    fig.update_yaxes(title_text="Acceleration Z", row=3, col=1)

    # Plot the figure
    chart_placeholder.plotly_chart(fig, use_container_width=True)

else:
    st.write("Waiting for data...")

# Add a refresh mechanism
# Refresh the app every 1 second
st_autorefresh(interval=1000, key="data_refresh")

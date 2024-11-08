import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import os
import time

data_file = "data.csv"

# Initialize the plot
fig, ax = plt.subplots()
ax.set_title("Real-Time Accelerometer Data")
ax.set_xlabel("Logging Time")
ax.set_ylabel("Acceleration")
line_x, = ax.plot([], [], label="Acceleration X")
line_y, = ax.plot([], [], label="Acceleration Y")
line_z, = ax.plot([], [], label="Acceleration Z")
ax.legend()

# Define the update function
def update(frame):
    try:
        # Check if data file exists and is non-empty
        if os.path.isfile(data_file) and os.path.getsize(data_file) > 0:
            # Load the CSV file
            data = pd.read_csv(data_file)

            # Proceed only if we have data
            if not data.empty:
                # Extract the necessary columns
                x = data["loggingTime"]
                acc_x = data["accelerometerAccelerationX"]
                acc_y = data["accelerometerAccelerationY"]
                acc_z = data["accelerometerAccelerationZ"]

                # Update the line data
                line_x.set_data(x, acc_x)
                line_y.set_data(x, acc_y)
                line_z.set_data(x, acc_z)

                # Rescale the plot to fit the new data
                ax.relim()
                ax.autoscale_view()
    except Exception as e:
        print(f"Error updating plot: {e}")

# Create the animation and keep a strong reference to `ani`
ani = FuncAnimation(
    fig,
    update,
    interval=1000,
    cache_frame_data=False  # Suppress the cache warning
)

# Display the plot and keep `ani` in memory
plt.show()

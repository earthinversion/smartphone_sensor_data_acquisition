#!/bin/bash

# Find and kill the TCP server process
pkill -f "python tcp_server_db.py"

# # Find and kill the Streamlit app process
# pkill -f "streamlit run streamlit_app.py"
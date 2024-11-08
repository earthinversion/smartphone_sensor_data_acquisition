#!/bin/bash

# Run the TCP server script in the background
nohup python tcp_server_db.py > tcp_server.log 2>&1 &

# Run the Streamlit app on port 5000 in the background
# streamlit run streamlit_app.py --server.port 5000
# nohup streamlit run streamlit_app.py --server.port 5000 > streamlit_app.log 2>&1 &

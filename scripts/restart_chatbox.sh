#!/usr/bin/env bash

# The script takes the following positional parameters:
#  - new IP address
#  - new subfolder of archive_logs (year_month format, e.g., 2023_09)

echo -e "\nRestart process started. Working in the following directory:"
pwd .
#cd git/ChatBox

# Kill all python processes (should be http and chatbox servers)
python_PIDs=$( pidof python )
kill $python_PIDs
echo -e "\nKilled sessions: $python_PIDs"

# Update the server's address
sed -i "s/SERVER_ADDRESS = .*/SERVER_ADDRESS = $1/" server_http/static/config.js
echo -e "\nUpdated server address:"
sed -n 1p server_http/static/config.js

# Move the logs file to the most recent folder in archive
last_dir=$( ls -rt logs_archive | tail -n 1 )
mv logs.log logs_archive/$last_dir
echo -e "\nChatbox server logs moved to logs_archive/$last_dir"

# Create new dir with name defined as parameter
logs_dir="logs_archive/$2"
mkdir "$logs_dir"

# Start http server and save log file in the above folder
python -m server_http.endpoints >> $logs_dir/http_logs.logs 2>&1 &
echo -e "\nServer http started. Logs are being saved in $logs_dir"

# Start chatbox server
python -m src.chatbox_websocket_server chatbox_config.json &
echo -e "\nChatbox server started"

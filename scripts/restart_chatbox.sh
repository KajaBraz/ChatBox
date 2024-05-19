#!/usr/bin/env bash

source restart.config

echo -e "\nRestart process started. Working in the following directory:"
pwd .

# Kill all python processes (should be http and chatbox servers)
python_PIDs=$( pidof python )
echo -e "\nKill sessions: $python_PIDs"
kill $python_PIDs

# Restore all modified files
git diff > diff.txt
git restore .

# Pull latest changes
echo -e "\nPull latest changes"
git pull

# Get current ip address
ip_address=$( curl ifconfig.me/ip )
echo -e "\nGet IP address: $ip_address"

# Update the server's address
echo -e "\nUpdate server address:"
sed -i "s/SERVER_ADDRESS = .*/SERVER_ADDRESS = $ip_address/" server_http/static/config.js
sed -n 1p server_http/static/config.js

# Update config data
echo -e "\nUpdate config data"
sed -i "s/\"name\": .*/\"name\": \"0.0.0.0\",/" chatbox_config.json

# Update Flask data
echo -e "\nUpdate Flask data"
sed -i "s/app.run()/app.run(host='0.0.0.0', port='11000')/" server_http/endpoints.py

# Move the logs file to the most recent folder in archive
last_dir=$( ls -rt logs_archive | tail -n 1 )
echo -e "\nMove Chatbox server logs to logs_archive/$last_dir"
mv logs.log logs_archive/$last_dir

# Create new dir with name defined as parameter
logs_dir="logs_archive/$new_logs_subdirectory"
mkdir "$logs_dir"

# Start http server and save log file in the above folder
python -m server_http.endpoints >> $logs_dir/http_logs.logs 2>&1 &
echo -e "\nServer http started. Logs are being saved in $logs_dir"

# Start chatbox server
python -m src.chatbox_websocket_server chatbox_config.json &
echo -e "\nChatbox server started"

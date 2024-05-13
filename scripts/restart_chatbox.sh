#!/usr/bin/env bash

# The script takes the following positional parameters:
#  - new IP address
#  - new subfolder of archive_logs (year_month format, e.g., 2023_09)
#  - database login
#  - database password
#  - database name

echo -e "\nRestart process started. Working in the following directory:"
pwd .
#cd git/ChatBox

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

# Update the server's address
echo -e "\nUpdate server address:"
sed -i "s/SERVER_ADDRESS = .*/SERVER_ADDRESS = $1/" server_http/static/config.js
sed -n 1p server_http/static/config.js

# Update config data
echo -e "\nUpdate config data:"
sed -i "s/\"db_login\": .*/\"db_login\": \"$3\",/" chatbox_config.json
sed -i "s/\"db_password\": .*/\"db_password\": \"$4\",/" chatbox_config.json
sed -i "s/\"db_name\": .*/\"db_name\": \"$5\"/" chatbox_config.json
sed -i "s/\"name\": .*/\"name\": \"0.0.0.0\",/" chatbox_config.json

# Update Flask data
echo -e "\nUpdate Flask data:"
sed -i "s/app.run()/app.run(host='0.0.0.0', port='13297')/" server_http/endpoints.py

# Move the logs file to the most recent folder in archive
last_dir=$( ls -rt logs_archive | tail -n 1 )
echo -e "\nMove Chatbox server logs to logs_archive/$last_dir"
mv logs.log logs_archive/$last_dir

# Create new dir with name defined as parameter
logs_dir="logs_archive/$2"
mkdir "$logs_dir"

# Start http server and save log file in the above folder
python -m server_http.endpoints >> $logs_dir/http_logs.logs 2>&1 &
echo -e "\nServer http started. Logs are being saved in $logs_dir"

# Start chatbox server
python -m src.chatbox_websocket_server chatbox_config.json &
echo -e "\nChatbox server started"

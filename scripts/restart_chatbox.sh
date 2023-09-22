#!/usr/bin/env bash

# The script takes the following positional parameters:
#  - old IP address
#  - new IP address
#  - new subfolder of archive_logs (year_month format, e.g., 2023_09)

echo "\nRestart process started"
cd git/ChatBox

# Kill all python processes (should be http and chatbox servers)
python_PIDs=$( pidof python )
kill $python_PIDs
echo "Killed sessions: $python_PIDs"

# Update the url in .js
sed -i "s/$1/$2/" server_http/static/main_script.js
echo "Updated IPs server_http/static/main_script.js"

# Move the logs file to the most recent folder in archive
last_dir=$( ls -rt logs_archive | tail -n 1 )
mv logs.log logs_archive/$last_dir
echo "Chatbox server logs moved to logs_archive/$last_dir"

# Create new dir with name defined as parameter
logs_dir="logs_archive/$3"

# Start http server and save log file in the above folder
python -m server_http.endpoints >> $logs_dir/http_logs.logs 2>&1 $
echo "Server http started. Logs are being saved in $logs_dir"

# Start chatbox server
python -m src.chatbox_websocket_server chatbox_config.json &
echo "Chatbox server started\n"

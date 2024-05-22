#!/usr/bin/env bash

source scripts/restart_chatbox.config

cur_dir=$( pwd )

# Ensure working directory is the repository's main folder
if ! [[ ChatBox -eq $( basename $cur_dir ) ]]; then
  echo "\nIncorrect working directory ($cur_dir). Run the script from ChatBox main folder.";
  echo "Restart process could not be completed. Try again.";
  exit 1;
else
  echo -e "\nRestart process started. Working in the following directory: $cur_dir";
fi

# Save diff for reference
echo -e "\nWrite diff.txt file (note that the files not scanned for updates will be missing here)"
git diff > diff.txt

# Instruct git not to scan the config files for updates (treat them as unchanged)
echo -e "\nAvoid writing config files to the working directory"
git update-index --skip-worktree chatbox_config.json
git update-index --skip-worktree scripts/restart_chatbox.config

# Kill all python processes (two processes expected: http and chatbox servers)
python_PIDs=$( pidof python )
echo -e "\nKill sessions: $python_PIDs"
kill $python_PIDs

# Restore all modified files
git diff > diff.txt
git restore .

# Pull latest changes
echo -e "\nPull latest changes"
git pull
echo -e "\n"

# Get current ip address
ip_address=$( curl ifconfig.me/ip )
echo -e "\nGet IP address: $ip_address"

# Update the server's address
echo -e "\nUpdate server address:"
sed -i "s/SERVER_ADDRESS = .*/SERVER_ADDRESS = $ip_address:11000/" server_http/static/config.js
sed -n 1p server_http/static/config.js

# Update config data
echo -e "\nUpdate config data"
sed -i "s/\"name\": .*/\"name\": \"0.0.0.0\",/" chatbox_config.json

# Update Flask data
echo -e "\nUpdate Flask data"
sed -i "s/app.run()/app.run(host='0.0.0.0', port='13297')/" server_http/endpoints.py

# Add marker line to differentiate new version in log files
latest_commit=$( git log -n1 --pretty=format:%h )
logs_path_chatbox=$(  grep "log_file_name" chatbox_config.json | awk -F[\"\"] '{print $4}' )
cur_date=$( date )
echo -e "\n\n**** NEW VERSION ****\nRestart date: $cur_date\nLatest commit: $latest_commit\n\n" >> $logs_path_http
echo -e "\n\n**** NEW VERSION ****\nRestart date: $cur_date\nLatest commit: $latest_commit\n\n" >> $logs_path_chatbox

# Start http server
python -m server_http.endpoints >> $logs_path_http 2>&1 &
echo -e "\nServer http started. Logs are being saved in $logs_path_http"

# Start chatbox server
python -m src.chatbox_websocket_server chatbox_config.json 2>&1 &
echo -e "\nChatbox server started. Logs are being saved in $logs_path_chatbox"

echo -e "\nChatbox restart complete. Link: $ip_address:13297"

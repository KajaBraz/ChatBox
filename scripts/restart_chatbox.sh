#!/usr/bin/env bash

# Script which automates ChatBox deployment to production.
# On its execution, the latest changes from the repository are pulled and both the http and Chatbox servers are restarted.
# The script uses values defined in the following files: chatbox_config.json and scripts/restart_chatbox.config
# Script has to be executed from the ChatBox main directory

cur_dir=$( pwd )

# Ensure working directory is the repository's main directory
# Stop the execution if it is not
if ! [[ ChatBox == $( basename $cur_dir ) ]]; then
  echo "\nIncorrect working directory ($cur_dir). Run the script from ChatBox main directory.";
  echo "Restart process could not be completed. Try again.";
  exit 1;
fi

source scripts/restart_chatbox.config

echo -e "\nRestart process started. Working in the following directory: $cur_dir";

# Save diff for reference
echo -e "\nWrite diff.txt file (note that if there are any files not scanned for updates, they will be missing here)"
git diff > diff.txt

# Instruct git not to scan the config files for updates (treat them as unchanged in order to preserve config values)
# This is required in order to be able to execute "git restore" and "git pull" but will be undone afterwards
git update-index --skip-worktree chatbox_config.json
git update-index --skip-worktree scripts/restart_chatbox.config

# Kill all python processes (two processes expected: http and chatbox servers)
python_PIDs=$( pidof python )
echo -e "\nKill sessions: $python_PIDs"
kill $python_PIDs

# Restore all modified files
git restore .

# Pull latest changes
echo -e "\nPull latest changes"
git pull
echo -e "\n"

# Undo ignoring config files (include previously excluded files in order to avoid potential confusion)
git update-index --no-skip-worktree chatbox_config.json
git update-index --no-skip-worktree scripts/restart_chatbox.config

# Get current ip address
ip_address=$( curl ifconfig.me/ip )
echo -e "\nGet IP address: $ip_address"

# Update the server's address
echo -e "\nUpdate server address:"
sed -i "s/SERVER_ADDRESS = .*/SERVER_ADDRESS = \"$ip_address:11000\";/" server_http/static/config.js
sed -n 1p server_http/static/config.js

# Update config data
echo -e "\nUpdate config data"
sed -i "s/\"name\": .*/\"name\": \"0.0.0.0\",/" chatbox_config.json

# Update Flask data
echo -e "\nUpdate Flask data"
sed -i "s/app.run()/app.run(host='0.0.0.0', port='$port')/" server_http/endpoints.py

# Add marker line to differentiate new version in log files
latest_commit=$( git log -n1 --pretty=format:%h )
logs_path_chatbox=$(  grep "log_file_name" chatbox_config.json | awk -F[\"\"] '{print $4}' )
cur_date=$( date )
echo -e "\n\n**** NEW VERSION ****\n\tRestart date:\t$cur_date\n\tLatest commit:\t$latest_commit\n\n" >> $logs_path_http
echo -e "\n\n**** NEW VERSION ****\n\tRestart date:\t$cur_date\n\tLatest commit:\t$latest_commit\n\n" >> $logs_path_chatbox

# Start http server
python -m server_http.endpoints >> $logs_path_http 2>&1 &
echo -e "\nServer http started. Logs are being saved in $logs_path_http"

# Start chatbox server
python -m src.chatbox_websocket_server chatbox_config.json 2>&1 &
echo -e "\nChatbox server started. Logs are being saved in $logs_path_chatbox"

echo -e "\nChatbox restart complete. Link: $ip_address:$port"

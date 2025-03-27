#!/bin/bash

# Get the current script's directory
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
server_dir="$script_dir/../../../src/agt_server/server/"
agent_dir="$script_dir/../../../src/agt_server/agents/test_agents/sa"
venv_activation_script="$script_dir/../../../.venv/bin/activate"
ip_address="10.39.0.22"


# Open new tabs in Terminal and execute commands
osascript -e 'tell application "Terminal" to activate' 

osascript -e 'tell application "Terminal" to activate' \
          -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Server"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$server_dir'; clear; python server.py sa_config.json --ip '$ip_address'\" in selected tab" \

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "First Price Agent"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python fp_bidder/my_agent.py  --join_server  --ip '$ip_address'\" in selected tab" \

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Over Bidding Agent"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python over_bidder/my_agent.py  --join_server  --ip '$ip_address'\" in selected tab" \

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Random Agent"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python random_bidder/my_agent.py  --join_server  --ip '$ip_address'\" in selected tab" \

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Truthful Agent"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python truth_bidder/my_agent.py  --join_server  --ip '$ip_address'\" in selected tab" \

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Bad Bid Agent"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python bad_bid/my_agent.py  --join_server  --ip '$ip_address'\" in selected tab" \

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Bad Update Agent"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python bad_update/my_agent.py  --join_server  --ip '$ip_address'\" in selected tab" \
        
osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Bad Setup Agent"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python bad_setup/my_agent.py  --join_server  --ip '$ip_address'\" in selected tab" 
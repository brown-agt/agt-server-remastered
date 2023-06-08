#!/bin/bash

# Get the current script's directory
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
server_dir="$script_dir/../../../src/server/"
agent_dir="$script_dir/../../../src/agt_agents/agents/test_agents/bos"
ip_address="192.168.1.16"

# Open new tabs in Terminal and execute commands
osascript -e 'tell application "Terminal" to activate' \
          -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Server"' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$server_dir'; cd ../../../src/server/; clear; python server.py bos_config.json\" in selected tab" \

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Compromising Agent"' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python always_compromise/my_agent.py CompromisingAgent --run_server --ip '$ip_address'\" in selected tab" \

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Stubborn Agent"' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python always_stubborn/my_agent.py StubbornAgent --run_server --ip '$ip_address'\" in selected tab" \

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Random Agent"' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python random_agent/my_agent.py Random --run_server --ip '$ip_address'\" in selected tab" \

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Punitive Agent"' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python punitive_agent/my_agent.py PunitiveAgent --run_server --ip '$ip_address'\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Reluctant Agent"' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python reluctant_agent/my_agent.py ReluctantAgent --run_server --ip '$ip_address'\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Anti Punitive Agent"' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python anti_punitive/my_agent.py AntiPunitiveAgent --run_server --ip '$ip_address'\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Fishing Chip Agent"' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python fishing_chip/my_agent.py FishingChip --run_server --ip '$ip_address'\" in selected tab"


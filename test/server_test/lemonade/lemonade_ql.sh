#!/bin/bash

# Get the current script's directory
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
server_dir="$script_dir/../../../src/agt_server/server/"
agent_dir="$script_dir/../../../src/agt_server/agents/test_agents/lemonade"
venv_activation_script="$script_dir/../../../.venv/bin/activate"
ip_address="10.38.61.67"

# Open new tabs in Terminal and execute commands
osascript -e 'tell application "Terminal" to activate' \
          -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Server"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$server_dir'; cd ../../../src/server/; clear; python server.py lemonade_config.json\" in selected tab" \

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Random Seed Agent1"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python always_stay/my_agent.py StaticRandom1 --join_server --ip '$ip_address'\" in selected tab" \

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Random Seed Agent2"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python always_stay/my_agent.py StaticRandom2 --join_server --ip '$ip_address'\" in selected tab" \

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "BestRespondAgent1 Agent"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python best_respond_agent/my_agent.py BestRespondAgent1 --join_server --ip '$ip_address'\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "BestRespondAgent2 Agent"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python best_respond_agent/my_agent.py BestRespondAgent2 --join_server --ip '$ip_address'\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Random Agent1"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python random_agent/my_agent.py Random1 --join_server --ip '$ip_address'\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Random Agent2"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python random_agent/my_agent.py Random2 --join_server --ip '$ip_address'\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Decremental Agent1"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python decrement_agent/my_agent.py DecrementalAgent1 --join_server --ip '$ip_address'\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Decremental Agent2"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python decrement_agent/my_agent.py DecrementalAgent2 --join_server --ip '$ip_address'\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Incremental Agent1"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python increment_agent/my_agent.py IncrementalAgent1 --join_server --ip '$ip_address'\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Incremental Agent2"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python increment_agent/my_agent.py IncrementalAgent2 --join_server --ip '$ip_address'\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Stick Agent1"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python stick_agent/my_agent.py StickAgent1 --join_server --ip '$ip_address'\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Stick Agent2"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python stick_agent/my_agent.py StickAgent2 --join_server --ip '$ip_address'\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "E2A Agent"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python end_to_end_agent/my_agent.py E2A --join_server --ip '$ip_address'\" in selected tab"
    
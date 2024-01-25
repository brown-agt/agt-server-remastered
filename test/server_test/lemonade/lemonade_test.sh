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
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Random Seed Agent"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python always_stay/my_agent.py StaticRandom --join_server --ip '$ip_address'\" in selected tab" \

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "BestRespondAgent Agent"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python best_respond_agent/my_agent.py BestRespondAgent --join_server --ip '$ip_address'\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Circular Hotel Agent"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python circular_hotel/my_agent.py CircularHotel --join_server --ip '$ip_address'\" in selected tab" \

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Decremental Agent"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python decrement_agent/my_agent.py DecrementalAgent --join_server --ip '$ip_address'\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Del Agent"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python del_agent/my_agent.py DelAgent --join_server --ip '$ip_address'\" in selected tab" \

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Dumb Chicken"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python dumb_chicken/my_agent.py DumbChicken --join_server --ip '$ip_address'\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "E2A Agent"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python end_to_end_agent/my_agent.py E2A --join_server --ip '$ip_address'\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Etch Agent"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python etch_agent/my_agent.py EtchAgent --join_server --ip '$ip_address'\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Eyes Out Agent"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python eyes_out/my_agent.py Eyes --join_server --ip '$ip_address'\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Good Bot Agent"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python good_bot/my_agent.py GoodBot --join_server --ip '$ip_address'\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Hi Bot Agent"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python hi_bot/my_agent.py HiBot --join_server --ip '$ip_address'\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Incremental Agent"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python incremental_agent/my_agent.py IncrementalAgent --join_server --ip '$ip_address'\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Jimbus"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python jimbus/my_agent.py Jimbus --join_server --ip '$ip_address'\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Kamen Rider"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python kamen_rider/my_agent.py Kamen --join_server --ip '$ip_address'\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Q Agent"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python q_agent/my_agent.py QQQ --join_server --ip '$ip_address'\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Random Agent"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python random_agent/my_agent.py Random --join_server --ip '$ip_address'\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Spinner"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python spinner/my_agent.py Spinner --join_server --ip '$ip_address'\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Bad Move"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python st_bad_move/my_agent.py STBadMove --join_server --ip '$ip_address'\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Stick Agent"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python stick_agent/my_agent.py StickAgent --join_server --ip '$ip_address'\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Sticky Agent"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python sticky/my_agent.py Sticky --join_server --ip '$ip_address'\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Team Player"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python team_player/my_agent.py TeamPlayer --join_server --ip '$ip_address'\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Zenly Agent"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python zenly/my_agent.py Zenly --join_server --ip '$ip_address'\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Bad Move Agent"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python st_bad_move/my_agent.py BadMove --join_server --ip '$ip_address'\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Bad Type Agent"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python st_bad_type/my_agent.py BadType --join_server --ip '$ip_address'\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Thinking Agent"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python st_delay/my_agent.py Thinker --join_server --ip '$ip_address'\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Bad Connection Agent"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python st_disconnect/my_agent.py BadConnection --join_server --ip '$ip_address'\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Long Name Agent"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python st_flood/my_agent.py Flood --join_server --ip '$ip_address'\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Math Breaking Agent"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python st_math_err/my_agent.py MathBreaker --join_server --ip '$ip_address'\" in selected tab"

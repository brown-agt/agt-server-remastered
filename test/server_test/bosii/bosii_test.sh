#!/bin/bash

# Get the current script's directory
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
server_dir="$script_dir/../../../src/agt_server/server/"
agent_dir="$script_dir/../../../src/agt_server/agents/test_agents/bosii"
venv_activation_script="$script_dir/../../../.venv/bin/activate"
ip_address="172.20.138.17"

# Open new tabs in Terminal and execute commands
osascript -e 'tell application "Terminal" to activate' \
          -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Server"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$server_dir'; cd ../../../src/server/; clear; python server.py bosii_config.json\" in selected tab" \

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Compromising Agent"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python always_compromise/my_agent.py CompromisingAgent --join_server --ip '$ip_address'\" in selected tab" \

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Stubborn Agent"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python always_stubborn/my_agent.py StubbornAgent --join_server --ip '$ip_address'\" in selected tab" \

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Random Agent"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python random_agent/my_agent.py Random --join_server --ip '$ip_address'\" in selected tab" \

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Punitive Agent"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python punitive_agent/my_agent.py PunitiveAgent --join_server --ip '$ip_address'\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Reluctant Agent"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python reluctant_agent/my_agent.py ReluctantAgent --join_server --ip '$ip_address'\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Anti Punitive Agent"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python anti_punitive/my_agent.py AntiPunitiveAgent --join_server --ip '$ip_address'\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Fishing Chip Agent"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python fishing_chip/my_agent.py FishingChip --join_server --ip '$ip_address'\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Ficticious Play Agent"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python ficticious_play/my_agent.py FicticiousPlay --join_server --ip '$ip_address'\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Exponential Agent"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python exponential/my_agent.py Exponential --join_server --ip '$ip_address'\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Reluctant Mood Agent"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python reluctant_mood_agent/my_agent.py ReluctantMoodAgent --join_server --ip '$ip_address'\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Punitive Mood Agent"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python punitive_mood_agent/my_agent.py PunitiveMoodAgent --join_server --ip '$ip_address'\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Mystery Agent"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python mystery/my_agent.py MysteryAgent --join_server --ip '$ip_address'\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Chipping Fish Agent"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python chipping_fish/my_agent.py ChippingFish --join_server --ip '$ip_address'\" in selected tab"

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

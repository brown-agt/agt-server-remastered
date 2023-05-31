#!/bin/bash

# Get the current script's directory
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
agent_dir="$script_dir/../../../src/agt_agents/agents/test_agents/rps"

# Open new tabs in Terminal and execute commands
osascript -e 'tell application "Terminal" to activate' 

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Exponential Agent"' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python exponential.py Exponential\" in selected tab" \

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Ficticious Play Agent"' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python ficticious_play.py FicticiousPlay\" in selected tab" \

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Random Agent"' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python random_agent.py Random\" in selected tab" \

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Rock Loving Agent"' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python rock_lover.py RockLover\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Bad Move Agent"' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python st_bad_move.py BadMove\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Bad Type Agent"' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python st_bad_type.py BadType \" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Thinking Agent"' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python st_delay.py Thinker \" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Bad Connection Agent"' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python st_disconnect.py BadConnection \" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Long Name Agent"' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python st_flood.py \" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Math Breaking Agent"' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python st_math_err.py MathBreaker \" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "TA Agent"' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python ta_agent.py TA \" in selected tab"
#!/bin/bash

# Get the current script's directory
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
server_dir="$script_dir/../../../src/server/"
agent_dir="$script_dir/../../../src/agt_agents/agents/test_agents/chicken"
ip_address="192.168.1.16"

# Open new tabs in Terminal and execute commands
osascript -e 'tell application "Terminal" to activate' \
          -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Server"' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$server_dir'; cd ../../../src/server/; clear; python server.py chicken_config.json\" in selected tab" \

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Exponential Agent"' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python exponential/my_agent.py Exponential --run_server --ip '$ip_address'\" in selected tab" \

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Ficticious Play Agent"' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python ficticious_play/my_agent.py FicticiousPlay --run_server --ip '$ip_address'\" in selected tab" \

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Random Agent"' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python random_agent/my_agent.py Random --run_server --ip '$ip_address'\" in selected tab" \

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Swerve Agent"' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python always_swerve/my_agent.py SwerveAgent --run_server --ip '$ip_address'\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Continue Agent"' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python always_continue/my_agent.py ContinueAgent --run_server --ip '$ip_address'\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Bad Move Agent"' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python st_bad_move/my_agent.py BadMove --run_server --ip '$ip_address'\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Bad Type Agent"' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python st_bad_type/my_agent.py BadType --run_server --ip '$ip_address'\" in selected tab"

# osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
#           -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Thinking Agent"' \
#           -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python st_delay/my_agent.py Thinker --run_server --ip '$ip_address'\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Bad Connection Agent"' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python st_disconnect/my_agent.py BadConnection --run_server --ip '$ip_address'\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Long Name Agent"' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python st_flood/my_agent.py --run_server --ip '$ip_address'\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Basic Agent"' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python basic_agent/my_agent.py BasicAgent --run_server --ip '$ip_address'\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Mystery Agent"' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python mystery_agent/my_agent.py MysteryAgent --run_server --ip '$ip_address'\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Math Breaking Agent"' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python st_math_err/my_agent.py MathBreaker --run_server --ip '$ip_address'\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Static Lastmove Agent"' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python lastmove_chicken/my_agent.py LastMoveStaticAgent --run_server --ip '$ip_address' --train False --save_path lastmove_chicken/qtable_static.npy\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Lastmove Agent"' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python lastmove_chicken/my_agent.py LastMoveAgent --run_server --ip '$ip_address'  --save_path lastmove_chicken/qtable.npy\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Static Lookback Agent"' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python lookback_chicken/my_agent.py LookBackStaticAgent --run_server --ip '$ip_address' --train False --save_path lookback_chicken/qtable_static.npy\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Lookback Agent"' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python lookback_chicken/my_agent.py LookBackAgent --run_server --ip '$ip_address'  --save_path lookback_chicken/qtable.npy\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Static QLearning Agent"' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python ql_chicken/my_agent.py QLearningStaticAgent --run_server --ip '$ip_address' --train False --save_path ql_chicken/qtable_static.npy\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "QLearning Agent"' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python ql_chicken/my_agent.py QLearningAgent --run_server --ip '$ip_address'  --save_path ql_chicken/qtable.npy\" in selected tab"
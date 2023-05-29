#!/bin/bash

# Get the current script's directory
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Open new tabs in Terminal and execute commands
osascript -e 'tell application "Terminal" to activate' \
          -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Server"' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$script_dir'; cd ../../../../server/; clear; python server.py server_configs/chicken_config.json\" in selected tab" \

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Exponential Agent"' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$script_dir'; clear; python exponential.py Exponential --run_server\" in selected tab" \

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Ficticious Play Agent"' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$script_dir'; clear; python ficticious_play.py FicticiousPlay --run_server\" in selected tab" \

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Random Agent"' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$script_dir'; clear; python random_agent.py Random --run_server\" in selected tab" \

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Swerve Agent"' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$script_dir'; clear; python always_swerve.py SwerveAgent --run_server\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Continue Agent"' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$script_dir'; clear; python always_continue.py ContinueAgent --run_server\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Bad Move Agent"' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$script_dir'; clear; python st_bad_move.py BadMove --run_server\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Bad Type Agent"' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$script_dir'; clear; python st_bad_type.py BadType --run_server\" in selected tab"

# osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
#           -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Thinking Agent"' \
#           -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$script_dir'; clear; python st_delay.py Thinker --run_server\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Bad Connection Agent"' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$script_dir'; clear; python st_disconnect.py BadConnection --run_server\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Long Name Agent"' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$script_dir'; clear; python st_flood.py --run_server\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Math Breaking Agent"' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$script_dir'; clear; python st_math_err.py MathBreaker --run_server\" in selected tab"


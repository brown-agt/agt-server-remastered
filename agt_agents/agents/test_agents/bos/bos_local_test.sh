#!/bin/bash

# Get the current script's directory
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Open new tabs in Terminal and execute commands
osascript -e 'tell application "Terminal" to activate' 

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Compromising Agent"' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$script_dir'; clear; python always_compromise.py CompromisingAgent\" in selected tab" \

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Stubborn Agent"' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$script_dir'; clear; python always_stubborn.py StubbornAgent\" in selected tab" \

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Random Agent"' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$script_dir'; clear; python random_agent.py Random\" in selected tab" \

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Punitive Agent"' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$script_dir'; clear; python punitive_agent.py PunitiveAgent\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Reluctant Agent"' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$script_dir'; clear; python reluctant_agent.py ReluctantAgent\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Anti Punitive Agent"' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$script_dir'; clear; python anti_punitive.py AntiPunitiveAgent\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Fishing Chip Agent"' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$script_dir'; clear; python fishing_chip.py FishingChip\" in selected tab"


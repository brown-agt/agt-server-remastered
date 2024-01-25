#!/bin/bash

# Get the current script's directory
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
agent_dir="$script_dir/../../../src/agt_server/agents/test_agents/chicken"
venv_activation_script="$script_dir/../../../.venv/bin/activate"

# Open new tabs in Terminal and execute commands
osascript -e 'tell application "Terminal" to activate' 

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Exponential Agent"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python exponential/my_agent.py Exponential \" in selected tab" \

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Ficticious Play Agent"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python ficticious_play/my_agent.py FicticiousPlay\" in selected tab" \

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Random Agent"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python random_agent/my_agent.py Random\" in selected tab" \

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Swerve Agent"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python always_swerve/my_agent.py SwerveAgent\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Continue Agent"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python always_continue/my_agent.py ContinueAgent\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Bad Move Agent"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python st_bad_move/my_agent.py BadMove\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Bad Type Agent"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python st_bad_type/my_agent.py BadType\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Thinking Agent"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python st_delay/my_agent.py Thinker\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Bad Connection Agent"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python st_disconnect/my_agent.py BadConnection\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Long Name Agent"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python st_flood/my_agent.py\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Math Breaking Agent"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python st_math_err/my_agent.py MathBreaker\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Basic Agent"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python basic_agent/my_agent.py BasicAgent\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Mystery Agent"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python mystery_agent/my_agent.py MysteryAgent\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Lastmove Agent"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python lastmove_chicken/my_agent.py LastMoveAgent\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Lastmove Agent"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python lastmove_chicken/my_agent.py LastMoveStaticAgent --train False --save_path lastmove_chicken/qtable_static.npy\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Lookback Agent"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python lookback_chicken/my_agent.py LookBackAgent\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Static Lookback Agent"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python lookback_chicken/my_agent.py LookBackStaticAgent --train False --save_path lookback_chicken/qtable_static.npy\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "QLearning Agent"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python ql_chicken/my_agent.py QLearningAgent\" in selected tab"

osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
          -e 'tell application "Terminal" to set custom title of selected tab of the front window to "Static QLearning Agent"' \
          -e 'tell application "Terminal" to do script "source \"'"$venv_activation_script"'\";" in window 1' \
          -e "tell application \"Terminal\" to tell window 1 to do script \"cd '$agent_dir'; clear; python ql_chicken/my_agent.py QLearningStaticAgent --train False --save_path ql_chicken/qtable_static.npy\" in selected tab"
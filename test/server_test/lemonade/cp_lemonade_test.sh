#!/bin/bash

# Configurable Paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVER_DIR="$(realpath "$SCRIPT_DIR/../../../src/agt_server/server/")"
AGENTS_DIR="$(realpath "$SCRIPT_DIR/../../../src/agt_server/agents/test_agents/lemonade_2025")"
VENV_ACTIVATION_SCRIPT="$(realpath "$SCRIPT_DIR/../../../.venv/bin/activate")"
LOG_DIR="$(realpath "$SCRIPT_DIR/lemonade_logs_2025")"
mkdir -p "$LOG_DIR"  # Ensure logs directory exists

# Use local IP for security
IP_ADDRESS="127.0.0.1"
SERVER_PORT=5000
PIDS=()  # Store process IDs

# Start the server in the background
source "$VENV_ACTIVATION_SCRIPT"
cd "$SERVER_DIR"
python3 server.py lemonade_config.json --ip "$IP_ADDRESS" --port "$SERVER_PORT" > "$LOG_DIR/server.log" 2>&1 &
SERVER_PID=$!
PIDS+=($SERVER_PID)

# Wait for the server to fully start
sleep 3 

TEMP_FILE=$(mktemp)
find "$AGENTS_DIR" -type f -name "my_agent.py" -print > "$TEMP_FILE"

# Read agent paths from the temp file
AGENT_SCRIPTS=()
while IFS= read -r file; do
    AGENT_SCRIPTS+=("$file")
done < "$TEMP_FILE"

# Remove the temporary file
rm -f "$TEMP_FILE"

# # Debugging: Print found agent scripts
echo "=== Found Agent Scripts ==="
printf '%s\n' "${AGENT_SCRIPTS[@]}"
echo "=========================="

# Start each agent in a fully isolated shell session
for AGENT_SCRIPT in "${AGENT_SCRIPTS[@]}"; do
    AGENT_DIR="$(dirname "$AGENT_SCRIPT")"  # Get absolute directory path
    AGENT_NAME="$(basename "$AGENT_DIR")"  # Get unique agent name
    LOG_FILE="$LOG_DIR/$AGENT_NAME.log"

    # echo "Starting agent in $AGENT_DIR (Logging: $LOG_FILE)"

    # Run in a new shell session & log output
    bash -c "cd '$AGENT_DIR' && source '$VENV_ACTIVATION_SCRIPT' && python3 my_agent.py --join_server --ip '$IP_ADDRESS' --port '$SERVER_PORT' > '$LOG_FILE' 2>&1" &

    PIDS+=($!)  # Store agent process PID
    sleep 1  # Staggered start for stability
done

# Wait for all processes to complete
for PID in "${PIDS[@]}"; do
    wait $PID
done

# Cleanup
echo "All agents finished. Cleaning up..."
kill "${PIDS[@]}" 2>/dev/null  # Kill any lingering processes
echo "Done."

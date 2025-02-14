#!/bin/bash

# Save the original directory
ORIGINAL_DIR=$(pwd)

# Change to the lemonade_2025 directory
cd ../../../src/agt_server/agents/test_agents/lemonade_2025 || { echo "Failed to cd into lemonade_2025"; exit 1; }

# Run merge_branches.sh
echo "Running merge_branches.sh..."
sh merge_branches.sh || { echo "merge_branches.sh failed"; exit 1; }

# Return to the original directory
cd "$ORIGINAL_DIR" || { echo "Failed to cd back to original directory"; exit 1; }

# Run cp_lemonade_test.sh
echo "Running cp_lemonade_test.sh..."
sh cp_lemonade_test.sh || { echo "cp_lemonade_test.sh failed"; exit 1; }

# Run update_leaderboard.py
echo "Running update_leaderboard.py..."
python3 update_leaderboard.py || { echo "update_leaderboard.py failed"; exit 1; }


cd "lemonade_logs_2025" || { echo "Failed to cd into lemonade_logs_2025"; exit 1; }

echo "Initializing submodule (if needed)..."
git submodule update --init --recursive || { echo "Submodule initialization failed"; exit 1; }

echo "Pushing results to lemonade_logs_2025..."
git add .
git commit -m "Update logs after leaderboard update"
git push origin main || { echo "Failed to push logs"; exit 1; }

cd "$ORIGINAL_DIR" || { echo "Failed to cd back to original directory"; exit 1; }

echo "All tasks completed successfully!"

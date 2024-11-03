#!/bin/bash

# Define an associative array mapping folder names to script filenames
declare -A folder_scripts=(
    ["ViewRequest"]="view_request.py"
    ["schedules"]="schedule.py"
    ["notification"]="notification.py"
    ["login"]="login.py"
    ["application-form"]="application-form.py"
)

# Paths and schedule for the autorejection cron job
PYTHON_SCRIPT="/home/project/spm-g2t8-dimsum-backend/autorejection/autorejection.py"
PYTHON_BIN="/usr/bin/python3"  # Adjust the path if needed
CRON_SCHEDULE="0 0 * * *"

# Step 1: Add the cron job for autorejection.py if it doesn't already exist
(crontab -l 2>/dev/null | grep -v "$PYTHON_SCRIPT"; echo "$CRON_SCHEDULE $PYTHON_BIN $PYTHON_SCRIPT") | crontab -
echo "Cron job added: Runs $PYTHON_SCRIPT daily at midnight."

# Step 2: Loop through each folder and execute the corresponding Python script
for folder in "${!folder_scripts[@]}"; do
    python_file="${folder}/${folder_scripts[$folder]}"

    # Check if there is an already running process for the same Python script
    pid=$(pgrep -f "$python_file")

    # If a process is running, terminate it
    if [ -n "$pid" ]; then
        echo "Terminating the currently running $python_file (PID: $pid)"
        kill -9 "$pid"
    fi

    # Check if the Python file exists
    if [ -f "$python_file" ]; then
        echo "Running $python_file ..."
        nohup python3 "$python_file" > "${python_file}.log" 2>&1 &
    else
        echo "$python_file does not exist, skipping this folder."
    fi
done

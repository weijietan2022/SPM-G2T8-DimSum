#!/bin/bash

# Define an associative array mapping folder names to script filenames
declare -A folder_scripts=(
    ["ViewRequest"]="view_request.py"
    ["schedules"]="schedule.py"
    ["notification"]="notification.py"
    ["login"]="login.py"
    ["autorejection"]="autorejection.py"
    ["application-form"]="application-form.py"
)

# Loop through each script and kill any running process
for folder in "${!folder_scripts[@]}"; do
    # Get the Python file to be killed for the current folder
    python_file="${folder}/${folder_scripts[$folder]}"

    # Find the process IDs of the running script (may return multiple PIDs)
    pids=$(pgrep -f "$python_file")

    # If any processes are running, terminate them
    if [ -n "$pids" ]; then
        for pid in $pids; do
            echo "Terminating $python_file (PID: $pid)"
            kill -9 "$pid"
        done
    else
        echo "$python_file is not currently running."
    fi
done

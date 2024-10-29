#!/bin/bash

# Define an associative array mapping folder names to script filenames
declare -A folder_scripts=(
    ["ViewRequest"]="view_request.py"
    ["schedules"]="schedule.py"
    ["notification"]="notification.py"
    ["login"]="login.py"
    ["autorejection"]="autorejection.py"
    ["application-form"]="application_form.py"
)

# Loop through each script and kill any running process
for folder in "${!folder_scripts[@]}"; do
    # Get the Python file to be killed for the current folder
    python_file="${folder}/${folder_scripts[$folder]}"

    # Find the process ID of the running script
    pid=$(pgrep -f "$python_file")

    # If a process is running, terminate it
    if [ -n "$pid" ]; then
        echo "Terminating $python_file (PID: $pid)"
        kill -9 "$pid"
    else
        echo "$python_file is not currently running."
    fi
done

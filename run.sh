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

# Loop through each folder and execute the corresponding Python script
for folder in "${!folder_scripts[@]}"; do
    # Get the Python file to be executed for the current folder
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
        python3 "$python_file" &
    else
        echo "$python_file does not exist, skipping this folder."
    fi
done

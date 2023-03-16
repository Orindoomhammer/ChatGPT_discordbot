#!/bin/bash

while true; do
    python3 ODH_Bot.py
    exit_status=$?
    if [ $exit_status -eq 0 ]; then
        echo "Bot exited normally. Restarting..."
    elif [ $exit_status -eq 1 ]; then
        echo "Bot exited with update signal. Updating and restarting..."
        git fetch --all
        git reset --hard origin/master
    else
        echo "Bot exited with status $exit_status. Stopping."
        break
    fi
done

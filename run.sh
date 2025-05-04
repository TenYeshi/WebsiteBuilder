#!/bin/bash

# Kill any existing process on port 5000
fuser -k 5000/tcp 2>/dev/null

# Start the application
python main.py
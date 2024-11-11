#!/bin/bash

echo "Starting Flask backend on port 5000"
# Run Flask (app.py) on port 5000 in the background
FLASK_APP=app.py flask run --host=0.0.0.0 --port=8080

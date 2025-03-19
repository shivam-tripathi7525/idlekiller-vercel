#!/bin/bash
export PORT=5001  # Ensure correct port
export FLASK_APP=api/app.py  # Flask entry point
flask run --host=0.0.0.0 --port=$PORT

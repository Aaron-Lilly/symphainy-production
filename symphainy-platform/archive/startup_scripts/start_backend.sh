#!/bin/bash
# Start backend server with proper PYTHONPATH

cd /home/founders/demoversion/symphainy_source/symphainy-platform
export PYTHONPATH=/home/founders/demoversion/symphainy_source/symphainy-platform:$PYTHONPATH
python3 main.py --port 8000



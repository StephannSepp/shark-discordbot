#!/bin/bash

exec python3 ./bot.py &
exec gunicorn --bind 0.0.0.0:8000 web:app
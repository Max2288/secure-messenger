#!/usr/bin/env bash

echo "Start service"

exec uvicorn src.app.main:create_app --host='0.0.0.0' --port='1026' --reload
#!/bin/bash
cd "$(dirname "$0")"
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python3 -m uvicorn main:app --reload --host 127.0.0.1 --port 8000

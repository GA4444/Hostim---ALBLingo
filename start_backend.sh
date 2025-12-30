#!/bin/bash
cd "$(dirname "$0")/backend"
source venv/bin/activate 2>/dev/null || python3 -m venv venv && source venv/bin/activate
pip install -q -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000



#!/bin/bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host localhost --port 9515

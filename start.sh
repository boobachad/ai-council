#!/bin/bash

cleanup() {
    echo -e "\nStopping frontend and backend servers"
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT

echo "backend: api.own-council.localhost"
source .venv/bin/activate
bun x portless api.own-council --force python -m backend.main &
BACKEND_PID=$!

echo "frontend: own-council.localhost"
cd frontend
bun x portless own-council --force bun run dev &
FRONTEND_PID=$!
cd ..

echo "ctrl+c toe exit"

wait $BACKEND_PID $FRONTEND_PID
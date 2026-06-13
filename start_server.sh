#!/bin/bash

PORT=5000

echo "===================================="
echo "   STARTING CMAD WEB SERVER + NGROK"
echo "===================================="

# --------------------------------------------------------
# 1. KILL ANYTHING ON PORT 5000
# --------------------------------------------------------
PID=$(lsof -t -i :$PORT)
if [ ! -z "$PID" ]; then
    echo "[0/3] Port $PORT in use by PID $PID — killing..."
    kill -9 $PID
    sleep 1
    echo "    → Freed port $PORT."
else
    echo "[0/3] Port $PORT is free."
fi

# --------------------------------------------------------
# 2. INSTALL GUNICORN IF MISSING
# --------------------------------------------------------
if ! command -v gunicorn &> /dev/null; then
    echo "[1/3] Installing Gunicorn..."
    pip install gunicorn --quiet
fi

# --------------------------------------------------------
# 3. START GUNICORN
#    -k gthread   → thread-based workers (fixes macOS fork crash)
#    --workers 1  → single process (no forking at all)
#    --threads 4  → 4 concurrent requests within that process
# --------------------------------------------------------
echo "[1/3] Starting Gunicorn (1 process, 4 threads)..."

gunicorn \
    --worker-class gthread \
    --workers 1 \
    --threads 4 \
    --bind 0.0.0.0:$PORT \
    --timeout 180 \
    --log-level info \
    app:app &

GUNICORN_PID=$!
sleep 5

if ! lsof -i :$PORT >/dev/null 2>&1; then
    echo "ERROR: Gunicorn failed to start. Check errors above."
    exit 1
fi
echo "    → Gunicorn running (PID $GUNICORN_PID)."

# --------------------------------------------------------
# 4. START NGROK
# --------------------------------------------------------
echo "[2/3] Starting ngrok tunnel..."
ngrok http $PORT > /dev/null 2>&1 &
sleep 4

# --------------------------------------------------------
# 5. GET PUBLIC URL
# --------------------------------------------------------
echo "[3/3] Fetching public URL..."
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | grep -o '"public_url":"[^"]*' | sed 's/"public_url":\"//')

if [ -z "$NGROK_URL" ]; then
    echo "WARNING: Could not fetch ngrok URL. Check http://localhost:4040"
else
    echo ""
    echo "========================================"
    echo "   CMAD WEBSITE IS LIVE!"
    echo "   Public URL: $NGROK_URL"
    echo "   Mode:       1 process / 4 threads"
    echo "========================================"
fi

echo ""
echo "Press CTRL+C to stop everything."
wait

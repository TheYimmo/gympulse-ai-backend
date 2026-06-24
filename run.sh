#!/usr/bin/env bash
set -e

API_PORT=8080
DASH_PORT=8501
API_LOG=/tmp/gympulse_api.log
DASH_LOG=/tmp/gympulse_dashboard.log

kill_port() {
    local port=$1
    local pid
    pid=$(lsof -ti tcp:"$port" 2>/dev/null || true)
    if [ -n "$pid" ]; then
        echo "  Killing process on :$port (PID $pid)"
        kill -9 $pid 2>/dev/null || true
        sleep 0.5
    fi
}

echo "==> Liberando puertos $API_PORT y $DASH_PORT..."
kill_port $API_PORT
kill_port $DASH_PORT

echo "==> Iniciando FastAPI en :$API_PORT..."
PYTHONPATH=. .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port $API_PORT > "$API_LOG" 2>&1 &
API_PID=$!

echo "    PID $API_PID · logs: $API_LOG"

echo "==> Esperando a que la API levante..."
for i in $(seq 1 20); do
    if curl -sf "http://localhost:$API_PORT/health" > /dev/null 2>&1; then
        echo "    API lista ✓"
        break
    fi
    sleep 0.5
done

echo "==> Iniciando Streamlit en :$DASH_PORT..."
GYMPULSE_API_URL="http://localhost:$API_PORT" \
PYTHONPATH=. \
.venv/bin/streamlit run dashboard/app.py \
    --server.port $DASH_PORT \
    --server.headless true \
    > "$DASH_LOG" 2>&1 &
DASH_PID=$!

echo "    PID $DASH_PID · logs: $DASH_LOG"

echo ""
echo "  GymPulse AI corriendo:"
echo "    API       → http://localhost:$API_PORT"
echo "    Docs      → http://localhost:$API_PORT/docs"
echo "    Dashboard → http://localhost:$DASH_PORT"
echo ""
echo "  Ctrl+C para detener ambos servicios."

trap "echo ''; echo 'Deteniendo...'; kill $API_PID $DASH_PID 2>/dev/null; exit 0" INT TERM

wait $API_PID $DASH_PID

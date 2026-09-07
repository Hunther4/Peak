#!/bin/bash

# ==============================================================
#  Peak Practice — Launcher
#  Corre en primer plano. Ctrl+C detiene todo.
# ==============================================================

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
export PYTHONPATH="$BACKEND_DIR"

NODE_BIN="/home/hunther4/.nvm/versions/node/v24.14.1/bin"
UVICORN="$BACKEND_DIR/venv/bin/uvicorn"

BACKEND_PID=""
FRONTEND_PID=""

cleanup() {
    echo -e "\n\033[0;31m🛑 Apagando Peak Practice...\033[0m"

    # Matar procesos si existen
    [ -n "$BACKEND_PID" ] && kill "$BACKEND_PID" 2>/dev/null
    [ -n "$FRONTEND_PID" ] && kill "$FRONTEND_PID" 2>/dev/null

    # También limpiar servicios systemd por si las dudas
    systemctl --user stop peak-backend 2>/dev/null
    systemctl --user stop peak-frontend 2>/dev/null

    echo -e "\033[0;32m✅ Detenido.\033[0m"
    exit 0
}
trap cleanup SIGINT SIGTERM

echo -e "\033[0;32m🚀 Iniciando Peak Practice...\033[0m"

# ── Seed ────────────────────────────────────────────────────
echo "🌱 Sembrando datos..."
"$BACKEND_DIR/venv/bin/python" "$BACKEND_DIR/seed.py"

# ── Matar servicios systemd previos ─────────────────────────
systemctl --user stop peak-backend peak-frontend 2>/dev/null

# ── Backend ────────────────────────────────────────────────
echo "📡 Levantando Backend en puerto 8000..."
"$UVICORN" main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Esperar a que el backend responda
for i in $(seq 1 10); do
    if curl -s http://localhost:8000/ > /dev/null 2>&1; then
        echo "   ✅ Backend listo"
        break
    fi
    if [ "$i" -eq 10 ]; then
        echo -e "   \033[0;31m❌ Backend no respondió\033[0m"
    fi
    sleep 1
done

# ── Frontend ───────────────────────────────────────────────
echo "🌐 Levantando Frontend en puerto 5173..."
cd "$FRONTEND_DIR" && PATH="$NODE_BIN:$PATH" pnpm exec vite --host 0.0.0.0 &
FRONTEND_PID=$!

# Esperar un toque a que el frontend arranque
sleep 3
echo "   ✅ Frontend listo (o arrancando)"

# ── Abrir navegador ────────────────────────────────────────
xdg-open "http://localhost:5173" 2>/dev/null || true

echo -e "\033[0;32m✅ ¡Sistema listo!\033[0m"
echo "👉 Backend:  http://localhost:8000"
echo "👉 Frontend: http://localhost:5173"
echo -e "💡 \033[1mCtrl+C\033[0m para detener todo."

# ── Esperar en primer plano ─────────────────────────────────
wait

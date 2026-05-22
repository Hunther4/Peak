#!/bin/bash

# ==============================================================
#  Peak Practice — Launcher
#  Uses systemd-run for resilient, detachable services.
#  Both backend and frontend survive terminal closes.
# ==============================================================

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
export PYTHONPATH="$BACKEND_DIR"

NODE_BIN="/home/hunther4/.nvm/versions/node/v24.14.1/bin"
UVICORN="$BACKEND_DIR/venv/bin/uvicorn"

cleanup() {
    echo -e "\n\033[0;31m🛑 Apagando Peak Practice...\033[0m"
    systemctl --user stop peak-backend 2>/dev/null
    systemctl --user stop peak-frontend 2>/dev/null
    echo -e "\033[0;32m✅ Detenido.\033[0m"
    exit
}
trap cleanup SIGINT SIGTERM

ensure_service() {
    local name="$1"
    local status
    status="$(systemctl --user is-active "$name" 2>/dev/null)"
    if [ "$status" = "active" ]; then
        echo "   ✅ $name ya está corriendo"
        return 0
    fi
    # Limpiar estado failed si existe
    systemctl --user reset-failed "$name" 2>/dev/null
    return 1
}

echo -e "\033[0;32m🚀 Iniciando Peak Practice...\033[0m"

# ── Seed ────────────────────────────────────────────────────
echo "🌱 Sembrando datos..."
"$BACKEND_DIR/venv/bin/python" seed.py

# ── Backend ────────────────────────────────────────────────
echo "📡 Levantando Backend en puerto 8000..."
if ! ensure_service peak-backend; then
    systemd-run --user --unit=peak-backend \
        --working-directory="$BACKEND_DIR" \
        -E PYTHONPATH="$BACKEND_DIR" \
        "$UVICORN" main:app --host 0.0.0.0 --port 8000
    sleep 1
    if [ "$(systemctl --user is-active peak-backend)" = "active" ]; then
        echo "   ✅ Backend listo"
    else
        echo -e "   \033[0;31m❌ Backend falló. Logs: journalctl --user -u peak-backend --no-pager -n 30\033[0m"
    fi
fi

# ── Frontend ───────────────────────────────────────────────
echo "🌐 Levantando Frontend en puerto 5173..."
if ! ensure_service peak-frontend; then
    systemd-run --user --unit=peak-frontend \
        --working-directory="$FRONTEND_DIR" \
        -E PATH="$NODE_BIN:/usr/bin:/bin" \
        "$NODE_BIN/pnpm" exec vite --host 0.0.0.0
    sleep 2
    if [ "$(systemctl --user is-active peak-frontend)" = "active" ]; then
        echo "   ✅ Frontend listo"
    else
        echo -e "   \033[0;31m❌ Frontend falló. Logs: journalctl --user -u peak-frontend --no-pager -n 30\033[0m"
    fi
fi

echo -e "\033[0;32m✅ ¡Sistema listo!\033[0m"
echo "👉 Backend:  http://localhost:8000"
echo "👉 Frontend: http://localhost:5173"
echo "💡 Ctrl+C para detener."
echo "   Logs: journalctl --user -u peak-backend --no-pager -n 30"

wait

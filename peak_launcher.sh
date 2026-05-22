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

cleanup() {
    echo -e "\n\033[0;31m🛑 Apagando Peak Practice...\033[0m"
    systemctl --user stop peak-backend 2>/dev/null
    systemctl --user stop peak-frontend 2>/dev/null
    echo -e "\033[0;32m✅ Detenido.\033[0m"
    exit
}
trap cleanup SIGINT SIGTERM

echo -e "\033[0;32m🚀 Iniciando Peak Practice...\033[0m"

# ── Backend ────────────────────────────────────────────────
echo "📡 Levantando Backend en puerto 8000..."
systemctl --user is-active peak-backend &>/dev/null && \
    echo "   ya está corriendo" || \
    systemd-run --user --unit=peak-backend \
        --working-directory="$BACKEND_DIR" \
        -E PYTHONPATH="$BACKEND_DIR" \
        /home/hunther4/Peak/backend/venv/bin/uvicorn main:app \
            --host 0.0.0.0 --port 8000 &>/dev/null

# ── Frontend ───────────────────────────────────────────────
echo "🌐 Levantando Frontend en puerto 5173..."
systemctl --user is-active peak-frontend &>/dev/null && \
    echo "   ya está corriendo" || \
    systemd-run --user --unit=peak-frontend \
        --working-directory="$FRONTEND_DIR" \
        /home/hunther4/.nvm/versions/node/v24.14.1/bin/pnpm exec vite \
            --host 0.0.0.0 &>/dev/null

echo -e "\033[0;32m✅ ¡Sistema listo!\033[0m"
echo "👉 Backend:  http://localhost:8000"
echo "👉 Frontend: http://localhost:5173"
echo "💡 Ctrl+C para detener. Los servicios se reinician solos si los matan."
echo "   Para ver logs: journalctl --user -u peak-backend --no-pager -n 50"

wait

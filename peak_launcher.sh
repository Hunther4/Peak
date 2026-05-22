#!/bin/bash

# Configuración de rutas
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

# Exportar PYTHONPATH para el backend
export PYTHONPATH="$BACKEND_DIR"

# Función de limpieza al cerrar
cleanup() {
    echo -e "\n\033[0;31m🛑 Apagando Peak Practice...\033[0m"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit
}

# Capturar Ctrl+C
trap cleanup SIGINT

echo -e "\033[0;32m🚀 Iniciando Peak Practice (Actualizando y cargando Full Stack)...\033[0m"

# 1. Iniciar Backend
echo "📡 Levantando Backend en puerto 8000..."
cd "$BACKEND_DIR"
uvicorn main:app --reload --port 8000 > /dev/null 2>&1 &
BACKEND_PID=$!

# 2. Iniciar Frontend de alta velocidad (con pnpm)
echo "🌐 Levantando Frontend de alta velocidad con pnpm..."
cd "$FRONTEND_DIR"
pnpm dev > /dev/null 2>&1 &
FRONTEND_PID=$!

echo -e "\033[0;32m✅ ¡Sistema listo!\033[0m"
echo "👉 Backend: http://localhost:8000"
echo "👉 Frontend: http://localhost:5173"
echo "💡 Presiona Ctrl+C para detener todo."

# Mantener el proceso padre vivo
wait

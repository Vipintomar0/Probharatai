#!/bin/bash
# Start ProBharatAI services
cd "$(dirname "$0")/.."

source venv/bin/activate 2>/dev/null

echo "🤖 Starting ProBharatAI..."

# Start backend
echo "🖥️  Starting backend on port 8000..."
cd backend && python main.py &
BACKEND_PID=$!
cd ..

# Start frontend
echo "⚛️  Starting frontend on port 3000..."
cd frontend && npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ ProBharatAI is running!"
echo "   Dashboard: http://localhost:3000"
echo "   API:       http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop."

# Trap Ctrl+C
trap "echo ''; echo 'Stopping...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM

wait

#!/bin/bash
set -e

echo "🚀 Asila Backend - Quick Start Script"
echo "======================================"

# Check if running in backend directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: Run this script from backend/ directory"
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your configuration"
fi

# Check if venv exists
if [ ! -d "../.venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv ../.venv
fi

# Activate venv
source ../.venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Check if PostgreSQL is running
echo "🔍 Checking PostgreSQL..."
if ! nc -z localhost 5432 2>/dev/null; then
    echo "⚠️  PostgreSQL not detected on localhost:5432"
    echo "   Start with: docker-compose up -d postgres"
fi

# Check if Redis is running
echo "🔍 Checking Redis..."
if ! nc -z localhost 6379 2>/dev/null; then
    echo "⚠️  Redis not detected on localhost:6379"
    echo "   Start with: docker-compose up -d redis"
fi

# Run migrations
echo "🗄️  Running database migrations..."
if nc -z localhost 5432 2>/dev/null; then
    alembic upgrade head || echo "⚠️  Migration failed - check DATABASE_URL in .env"
else
    echo "⏭️  Skipping migrations (no DB connection)"
fi

# Run tests
echo "🧪 Running tests..."
pytest -v || echo "⚠️  Some tests failed"

echo ""
echo "✅ Setup complete!"
echo ""
echo "Start the server:"
echo "  uvicorn app.main:app --reload --port 8000"
echo ""
echo "Or use Docker:"
echo "  docker-compose up -d"

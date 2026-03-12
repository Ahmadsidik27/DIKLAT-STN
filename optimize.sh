#!/usr/bin/env bash
# Production optimization script untuk STN-DIKLAT

echo "🔧 STN-DIKLAT Production Optimization"
echo "======================================"
echo ""

# 1. Environment check
echo "1. Checking environment..."
if [ -z "$FLASK_ENV" ]; then
    export FLASK_ENV=production
    echo "   ✅ FLASK_ENV set to: production"
fi

if [ -z "$PYTHONOPTIMIZE" ]; then
    export PYTHONOPTIMIZE=2
    echo "   ✅ PYTHONOPTIMIZE enabled"
fi

echo "   ✅ PYTHONUNBUFFERED enabled" 
export PYTHONUNBUFFERED=1

# 2. Database optimization
echo ""
echo "2. Database optimization..."
if command -v sqlite3 &> /dev/null; then
    echo "   ✅ Running SQLite VACUUM..."
    sqlite3 database/users.db "VACUUM;"
    sqlite3 database/users.db "PRAGMA optimize;"
    echo "   ✅ SQLite optimized"
fi

# 3. Clear caches
echo ""
echo "3. Clearing Python caches..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null
echo "   ✅ Python caches cleared"

# 4. Check disk space
echo ""
echo "4. Checking disk space..."
AVAILABLE_SPACE=$(df . | tail -1 | awk '{print $4}')
if [ "$AVAILABLE_SPACE" -lt 1048576 ]; then
    echo "   ⚠️  WARNING: Less than 1GB free disk space!"
    echo "      Available: $((AVAILABLE_SPACE / 1024))MB"
else
    echo "   ✅ Sufficient disk space: $((AVAILABLE_SPACE / 1024 / 1024))GB free"
fi

# 5. Summary
echo ""
echo "✅ Optimization complete!"
echo ""
echo "To start the application:"
echo "   docker-compose up -d --build"
echo ""
echo "To monitor logs:"
echo "   docker-compose logs -f"
echo ""

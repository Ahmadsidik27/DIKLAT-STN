#!/usr/bin/env bash
# Quick start script untuk STN-DIKLAT dengan Docker

set -e  # Exit on any error

echo "🚀 STN-DIKLAT Quick Start"
echo "========================="
echo ""

# 1. Check Docker
echo "1️⃣ Checking Docker..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker."
    exit 1
fi
echo "   ✅ Docker available: $(docker --version)"

# 2. Check Docker Compose
echo ""
echo "2️⃣ Checking Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose not found."
    exit 1
fi
echo "   ✅ Docker Compose available"

# 3. Check disk space
echo ""
echo "3️⃣ Checking disk space..."
DISK_FREE=$(df / | tail -1 | awk '{print $4}')
DISK_FREE_GB=$((DISK_FREE / 1024 / 1024))
echo "   Available: ${DISK_FREE_GB}GB"
if [ "$DISK_FREE_GB" -lt 2 ]; then
    echo "   ⚠️  WARNING: Low disk space! (<2GB free)"
    echo "   Run: bash cleanup.sh"
fi

# 4. Cleanup if needed
if [ -d "/home/codespace/.cache" ]; then
    CACHE_SIZE=$(du -sh /home/codespace/.cache 2>/dev/null | awk '{print $1}')
    if [ "$CACHE_SIZE" != "0" ]; then
        echo ""
        echo "4️⃣ Cleaning cache..."
        rm -rf /home/codespace/.cache
        mkdir -p /home/codespace/.cache
        echo "   ✅ Cache cleared"
    fi
fi

# 5. Check .env file
echo ""
echo "5️⃣ Checking configuration..."
if [ ! -f ".env" ]; then
    echo "   ❌ .env file not found!"
    exit 1
fi

# Verify Chroma Cloud config
if grep -q "CHROMA_CLOUD=true" .env; then
    echo "   ✅ Chroma Cloud enabled"
else
    echo "   ⚠️  Chroma Cloud not enabled"
fi

if grep -q "DISABLE_EMBEDDINGS_DOWNLOAD=true" .env; then
    echo "   ✅ Embeddings download disabled"
else
    echo "   ⚠️  Embeddings download enabled (may cause issues)"
fi

# 6. Stop existing container
echo ""
echo "6️⃣ Stopping existing container..."
docker-compose down 2>/dev/null || true
sleep 2
echo "   ✅ Stopped"

# 7. Build image
echo ""
echo "7️⃣ Building Docker image (this may take 2-5 minutes)..."
if docker-compose build --no-cache 2>&1 | tail -20; then
    echo "   ✅ Build successful"
else
    echo "   ❌ Build failed. Check errors above."
    exit 1
fi

# 8. Start container
echo ""
echo "8️⃣ Starting container..."
docker-compose up -d
echo "   ✅ Container started"

# 9. Wait for startup
echo ""
echo "9️⃣ Waiting for application startup (15 seconds)..."
sleep 15

# 10. Health check
echo ""
echo "🔟 Health check..."
for i in {1..10}; do
    if curl -s http://localhost:8000/ > /dev/null 2>&1; then
        echo "   ✅ Application is running!"
        echo ""
        echo "📊 Application Status:"
        docker-compose ps
        echo ""
        echo "🎉 SUCCESS! Access the app at http://localhost:8000/"
        echo ""
        echo "📖 View logs:"
        echo "   docker-compose logs -f"
        exit 0
    fi
    echo "   ⏳ Waiting... ($i/10)"
    sleep 2
done

echo "   ❌ Application not responding"
echo ""
echo "📋 Debugging info:"
echo "Container status:"
docker-compose ps
echo ""
echo "Recent logs:"
docker-compose logs | tail -30
exit 1

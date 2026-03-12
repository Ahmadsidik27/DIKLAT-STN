#!/usr/bin/env bash
# CRITICAL: Disk cleanup script - Remove disk space hogs immediately

echo "🔥 CRITICAL DISK CLEANUP - STN-DIKLAT"
echo "======================================"
echo ""

# Show current space
echo "BEFORE:"
df -h / | tail -1
echo ""

# 1. Clear all caches
echo "1️⃣ Clearing system caches..."
rm -rf /home/codespace/.cache 2>/dev/null
mkdir -p /home/codespace/.cache
echo "   ✅ Cleared user cache"

# 2. Clear package manager caches
echo ""
echo "2️⃣ Clearing package caches..."
rm -rf /var/lib/apt/lists/* 2>/dev/null
rm -rf /var/cache/apt/* 2>/dev/null
apt-get clean 2>/dev/null
echo "   ✅ APT cache cleaned"

# 3. Clear pip cache
echo ""  
echo "3️⃣ Clearing Python package cache..."
pip cache purge 2>/dev/null
echo "   ✅ PIP cache cleared"

# 4. Clear Docker layers
echo ""
echo "4️⃣ Cleaning Docker..."
docker system prune -af 2>/dev/null
docker volume prune -f 2>/dev/null
echo "   ✅ Docker cleaned"

# 5. Clear npm cache (if exists)
echo ""
echo "5️⃣ Clearing Node cache..."
npm cache clean --force 2>/dev/null
rm -rf ~/.npm 2>/dev/null
echo "   ✅ NPM cache cleared"

# 6. Clean build artifacts
echo ""
echo "6️⃣ Cleaning build artifacts..."
find /workspaces/DIKLAT-STN -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find /workspaces/DIKLAT-STN -type f -name "*.pyc" -delete 2>/dev/null
find /workspaces/DIKLAT-STN -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null
find /workspaces/DIKLAT-STN -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null
find /workspaces/DIKLAT-STN -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null
echo "   ✅ Build artifacts cleaned"

# 7. Clear tmp files
echo ""
echo "7️⃣ Clearing temp files..."
rm -rf /tmp/* 2>/dev/null
rm -rf /var/tmp/* 2>/dev/null
echo "   ✅ Temp files cleared"

# 8. Show final space
echo ""
echo "AFTER CLEANUP:"
df -h / | tail -1
AVAIL=$(df / | tail -1 | awk '{print $4}')
echo "Available: $((AVAIL / 1024 / 1024))GB free"
echo ""

if [ "$AVAIL" -gt 2097152 ]; then
    echo "✅ DISK SPACE HEALTHY (>2GB free)"
else
    echo "⚠️  WARNING: Still low on space (<2GB free)"
fi

echo ""
echo "Done! Application is ready to run."

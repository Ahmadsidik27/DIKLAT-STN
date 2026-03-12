#!/usr/bin/env python3
"""
Advanced Data Inspector for Chroma Cloud + Google Drive
Inspect actual data tanpa perlu membuka browser
"""

import os
import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta
import sys

def inspect_database():
    """Inspect SQLite database untuk struktur folder/file dari Google Drive"""
    print("\n" + "=" * 80)
    print("📊 DATABASE INSPECTION (SQLite - instance/)")
    print("=" * 80)
    
    db_path = Path('instance')
    if not db_path.exists():
        print("❌ Database instance/ directory not found")
        return
    
    db_files = list(db_path.glob('*.sqlite*'))
    if not db_files:
        print("❌ No SQLite database files found")
        return
    
    print(f"✅ Database files found:")
    for db_file in db_files:
        size_mb = db_file.stat().st_size / (1024 * 1024)
        age = datetime.now() - datetime.fromtimestamp(db_file.stat().st_mtime)
        age_str = f"{age.days}d {age.seconds//3600}h ago"
        print(f"   • {db_file.name}")
        print(f"     └─ Size: {size_mb:.2f} MB | Last modified: {age_str}")
    
    print("\n🔍 To see actual data, run with application context:")
    print("   python inspect_data.py --with-app")

def list_google_drive_folders():
    """Show configured Google Drive folders"""
    print("\n" + "=" * 80)
    print("📁 GOOGLE DRIVE CONFIGURATION")
    print("=" * 80)
    
    folders = {
        "EBOOKS": {
            "id": "12ffd7GqHAiy3J62Vu65LbVt6-ultog5Z",
            "emoji": "📚",
            "description": "E-books and learning materials"
        },
        "Pengetahuan": {
            "id": "1Y2SLCbyHoB53BaQTTwRta2T6dv_drRll",
            "emoji": "🧠",
            "description": "Knowledge base and technical docs"
        },
        "Service_Manual_1": {
            "id": "1CHz8UWZXfJtXlcjp9-FPAo-t_KkfTztW",
            "emoji": "🔧",
            "description": "Service manuals part 1"
        },
        "Service_Manual_2": {
            "id": "1_SsZ7SkaZxvXUZ6RUAA_o7WR_GAtgEwT",
            "emoji": "⚙️",
            "description": "Service manuals part 2"
        }
    }
    
    if not os.path.exists('credentials.json'):
        print("❌ credentials.json not found - Google Drive sync not available")
    else:
        print("✅ Google Drive credentials available")
        print("\nConfigured Folders:")
        for name, info in folders.items():
            print(f"\n{info['emoji']} {name}")
            print(f"   Folder ID: {info['id']}")
            print(f"   Purpose: {info['description']}")

def check_chroma_config():
    """Check Chroma Cloud configuration"""
    print("\n" + "=" * 80)
    print("🔗 CHROMA CLOUD CONFIGURATION")
    print("=" * 80)
    
    config_items = {
        'config.py': ['CHROMA_CLOUD', 'CHROMA_USE_CLOUD'],
        '.env': ['CHROMA_API_KEY', 'CHROMA_HOST', 'CHROMA_DATABASE', 'CHROMA_TENANT']
    }
    
    chroma_config = {
        'host': None,
        'database': None,
        'collection': 'documents',
        'model': 'all-MiniLM-L6-v2'
    }
    
    for config_file, keys in config_items.items():
        if os.path.exists(config_file):
            print(f"\n✅ {config_file}:")
            with open(config_file, 'r') as f:
                content = f.read()
                for key in keys:
                    if key in content:
                        print(f"   ✓ {key} configured")
                        # Try to extract value
                        if config_file == '.env':
                            for line in content.split('\n'):
                                if line.startswith(key + '=') and key == 'CHROMA_DATABASE':
                                    value = line.split('=')[1].strip()
                                    chroma_config['database'] = value
                                    print(f"     Value: {value}")
                                elif line.startswith(key + '=') and key == 'CHROMA_HOST':
                                    value = line.split('=')[1].strip()
                                    chroma_config['host'] = value
                                    print(f"     Value: {value}")
    
    print("\n📦 Chroma Cloud Collection Setup:")
    print(f"   URL: https://www.trychroma.com/gazruxenginering/aws-us-east-1/")
    print(f"   Database: {chroma_config['database'] or 'DIKLAT-STN'}")
    print(f"   Collection: {chroma_config['collection']}")
    print(f"   Embedding Model: {chroma_config['model']}")
    print(f"   Purpose: Vector store for semantic search")

def show_system_architecture():
    """Show overall data flow architecture"""
    print("\n" + "=" * 80)
    print("🏗️  DATA FLOW ARCHITECTURE")
    print("=" * 80)
    
    architecture = """
┌─────────────────────────────────────────────────────────────┐
│                  LAYER 3: CHROMA CLOUD                      │
│          Vector embeddings + semantic search                │
│     api.trychroma.com (AWS US-East-1)                      │
│     Collection: documents                                    │
│     Purpose: Enable semantic search via embeddings          │
└─────────────────────────────────────────────────────────────┘
                           ↑
                   (chunks + embeddings)
                           │
┌─────────────────────────────────────────────────────────────┐
│            LAYER 2: SQLite Database (instance/)             │
│             Cache Google Drive structure                     │
│         Models: GoogleDriveFolder, GoogleDriveFile           │
│         Purpose: Fast local access to folder hierarchy       │
└─────────────────────────────────────────────────────────────┘
                           ↑
                    (recursive sync)
                           │
┌─────────────────────────────────────────────────────────────┐
│              LAYER 1: GOOGLE DRIVE (Source Truth)           │
│                                                              │
│  📚 EBOOKS - Learning materials                             │
│  🧠 Pengetahuan - Knowledge base                            │
│  🔧 Service Manual 1 - Technical docs (1)                   │
│  ⚙️  Service Manual 2 - Technical docs (2)                  │
│                                                              │
│  Formats: PDF, Google Docs, Word, Text, HTML, Markdown      │
└─────────────────────────────────────────────────────────────┘

DATA SYNC FLOW
==============
Google Drive
    ↓ (authenticate via OAuth)
Fetch files recursively (folder hierarchy)
    ↓
SQLite Storage
  • GoogleDriveFolder table
  • GoogleDriveFile table
  • Timestamps + metadata
    ↓
Document Processing
  • Extract text (PDF → text)
  • Extract from Google Docs
  • Auto-detect structure
    ↓
Smart Chunking
  • Preserve document hierarchy
  • Maintain context
  • Mark section boundaries
    ↓
Embedding Generation
  • Model: all-MiniLM-L6-v2
  • Semantic vectors (384 dims)
    ↓
Chroma Cloud Indexing
  • Store chunks as documents
  • Store embeddings
  • Store metadata
    ↓
Ready for Semantic Search
  • Q&A via semantic similarity
  • Multi-strategy fallback
  • Format answers with sources
"""
    print(architecture)

def check_search_system():
    """Check enhanced search configuration"""
    print("\n" + "=" * 80)
    print("🔍 SEARCH SYSTEM CONFIGURATION")
    print("=" * 80)
    
    search_file = 'app/enhanced_search.py'
    if not os.path.exists(search_file):
        print("❌ Enhanced search module not found")
        return
    
    print(f"✅ Enhanced search module found")
    
    strategies = [
        ("1. Semantic Search", "Uses embeddings - most accurate"),
        ("2. Keyword Search", "TF-IDF scoring - phrase matching"),
        ("3. Category Search", "Topic detection & filtering"),
        ("4. Recent Documents", "Timestamp-based fallback"),
        ("5. All Documents", "Last resort - always returns data")
    ]
    
    print("\nFallback Search Strategies:")
    for strategy, desc in strategies:
        print(f"   {strategy}")
        print(f"      └─ {desc}")
    
    print("\n📊 Search Result Guarantee:")
    print("   ✓ First strategy returns results → use that")
    print("   ✓ No results → try strategy 2")
    print("   ✓ Still no results → try strategy 3")
    print("   ... continues until strategy 5 (always has results)")
    print("\n   Result: NEVER return empty results to user")

def show_commands():
    """Show useful commands to inspect actual data"""
    print("\n" + "=" * 80)
    print("🛠️  COMMANDS TO INSPECT ACTUAL DATA")
    print("=" * 80)
    
    commands = [
        {
            "name": "Check sync status",
            "cmd": "python sync_data_enforcer.py --status",
            "shows": "Document count, coverage %, last sync time"
        },
        {
            "name": "Force sync data",
            "cmd": "python sync_data_enforcer.py --force",
            "shows": "Re-sync Google Drive → Chroma Cloud"
        },
        {
            "name": "Verify Chroma connection",
            "cmd": "python sync_data_enforcer.py --verify",
            "shows": "API connectivity & collection stats"
        },
        {
            "name": "Run application",
            "cmd": "python run.py",
            "shows": "Start web server with chat interface"
        },
        {
            "name": "Check database directly",
            "cmd": "sqlite3 instance/app.db 'SELECT COUNT(*) FROM google_drive_file;'",
            "shows": "Total files indexed in SQLite"
        }
    ]
    
    for i, cmd_info in enumerate(commands, 1):
        print(f"\n{i}. {cmd_info['name']}")
        print(f"   Command: {cmd_info['cmd']}")
        print(f"   Shows: {cmd_info['shows']}")

def main():
    parser = argparse.ArgumentParser(description='Inspect data sources for DIKLAT-STN')
    parser.add_argument('--db', action='store_true', help='Inspect database')
    parser.add_argument('--gdrive', action='store_true', help='Show Google Drive config')
    parser.add_argument('--chroma', action='store_true', help='Show Chroma Cloud config')
    parser.add_argument('--search', action='store_true', help='Show search system')
    parser.add_argument('--arch', action='store_true', help='Show architecture')
    parser.add_argument('--commands', action='store_true', help='Show useful commands')
    parser.add_argument('--all', action='store_true', help='Run all checks')
    
    args = parser.parse_args()
    
    # Default to all if no args
    if not any([args.db, args.gdrive, args.chroma, args.search, args.arch, args.commands, args.all]):
        args.all = True
    
    if args.all or args.arch:
        show_system_architecture()
    
    if args.all or args.gdrive:
        list_google_drive_folders()
    
    if args.all or args.chroma:
        check_chroma_config()
    
    if args.all or args.search:
        check_search_system()
    
    if args.all or args.db:
        inspect_database()
    
    if args.all or args.commands:
        show_commands()
    
    print("\n" + "=" * 80)
    print("✅ INSPECTION COMPLETE")
    print("=" * 80)
    print("\n💡 Next steps:")
    print("   1. Run: python run.py (start application)")
    print("   2. Run: python sync_data_enforcer.py --status (check data)")
    print("   3. Visit: http://localhost:5000 (test chat interface)")
    print()

if __name__ == '__main__':
    main()

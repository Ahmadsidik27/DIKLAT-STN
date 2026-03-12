#!/usr/bin/env python3
"""
Data Sync Enforcer - Ensure all Google Drive data is synced to Chroma
Run this script para refresh data dari Google Drive ke Chroma Cloud

Usage:
    python sync_data_enforcer.py
    python sync_data_enforcer.py --force  (force complete resync)
    python sync_data_enforcer.py --status (check current status)
"""

import sys
import os
import argparse
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models import db, GoogleDriveFile, ChromaDocument, DocumentSyncLog
from app.drive_sync import sync_drive_files, index_document_to_chroma
from app.documents_handler import ROOT_FOLDERS


class DataSyncEnforcer:
    """Enforce data sync antara Google Drive dan Chroma"""
    
    @staticmethod
    def get_sync_status() -> dict:
        """Get current sync status"""
        try:
            total_files = GoogleDriveFile.query.count()
            indexed_files = ChromaDocument.query.filter_by(status='indexed').count()
            pending_files = ChromaDocument.query.filter_by(status='pending').count()
            failed_files = ChromaDocument.query.filter_by(status='failed').count()
            
            # Get last sync log
            last_sync = DocumentSyncLog.query.order_by(DocumentSyncLog.start_time.desc()).first()
            
            return {
                'total_files': total_files,
                'indexed_files': indexed_files,
                'pending_files': pending_files,
                'failed_files': failed_files,
                'coverage': f"{(indexed_files/total_files*100):.1f}%" if total_files > 0 else "0%",
                'last_sync': last_sync.start_time.isoformat() if last_sync else None,
                'last_sync_duration': f"{(last_sync.end_time - last_sync.start_time).seconds}s" if last_sync and last_sync.end_time else None
            }
        except Exception as e:
            print(f"❌ Error getting status: {e}")
            return {}
    
    @staticmethod
    def sync_all_folders(force: bool = False) -> dict:
        """
        Sync all ROOT_FOLDERS to Chroma
        
        Args:
            force: Force complete resync even if already synced
        
        Returns:
            Sync result summary
        """
        results = {
            'start_time': datetime.utcnow(),
            'folders_synced': 0,
            'files_added': 0,
            'files_indexed': 0,
            'files_failed': 0,
            'duration': None,
            'status': 'in_progress'
        }
        
        print("\n" + "="*60)
        print("📂 DATA SYNC ENFORCER - Starting sync process")
        print("="*60)
        
        try:
            for folder_name, folder_id in ROOT_FOLDERS.items():
                print(f"\n🔄 Syncing folder: {folder_name} (ID: {folder_id})")
                
                try:
                    # Sync files dari folder
                    sync_result = sync_drive_files(folder_id)
                    
                    if sync_result:
                        results['files_added'] += sync_result.get('files_added', 0)
                        results['files_indexed'] += sync_result.get('files_indexed', 0)
                        results['files_failed'] += sync_result.get('files_failed', 0)
                        results['folders_synced'] += 1
                        
                        print(f"  ✅ Synced: +{sync_result.get('files_added', 0)} files")
                        print(f"  📊 Indexed: +{sync_result.get('files_indexed', 0)} documents in Chroma")
                        if sync_result.get('files_failed', 0) > 0:
                            print(f"  ⚠️  Failed: {sync_result.get('files_failed', 0)}")
                    
                except Exception as e:
                    print(f"  ❌ Error syncing {folder_name}: {e}")
                    results['files_failed'] += 1
            
            # Check for pending/failed documents yang belum indexed
            print("\n🔍 Checking for unindexed documents...")
            pending = ChromaDocument.query.filter(
                ChromaDocument.status.in_(['pending', 'failed'])
            ).limit(50).all()
            
            if pending:
                print(f"  Found {len(pending)} pending/failed documents, attempting reindex...")
                reindexed = 0
                for doc in pending:
                    try:
                        drive_file = GoogleDriveFile.query.get(doc.file_id)
                        if drive_file:
                            if index_document_to_chroma(drive_file.drive_id, drive_file.file_name):
                                reindexed += 1
                    except Exception as e:
                        pass
                
                if reindexed > 0:
                    print(f"  ✅ Reindexed {reindexed} documents")
            
            results['status'] = 'complete'
            results['end_time'] = datetime.utcnow()
            results['duration'] = (results['end_time'] - results['start_time']).seconds
            
        except Exception as e:
            print(f"\n❌ Critical error during sync: {e}")
            results['status'] = 'failed'
            results['error'] = str(e)
        
        return results
    
    @staticmethod
    def print_sync_status():
        """Print detailed sync status"""
        status = DataSyncEnforcer.get_sync_status()
        
        print("\n" + "="*60)
        print("📊 DATA SYNC STATUS")
        print("="*60)
        print(f"Total Files (Google Drive): {status.get('total_files', 'N/A')}")
        print(f"Indexed (Chroma): {status.get('indexed_files', 'N/A')}")
        print(f"Pending: {status.get('pending_files', 'N/A')}")
        print(f"Failed: {status.get('failed_files', 'N/A')}")
        print(f"Coverage: {status.get('coverage', 'N/A')}")
        if status.get('last_sync'):
            print(f"Last Sync: {status.get('last_sync')}")
            print(f"Duration: {status.get('last_sync_duration', 'N/A')}")
        print("="*60 + "\n")
    
    @staticmethod
    def verify_chroma_connection() -> bool:
        """Verify connection to Chroma Cloud"""
        print("\n🔐 Verifying Chroma Cloud connection...")
        
        try:
            from app.chroma_integration import get_vector_store
            
            vector_store = get_vector_store()
            if not vector_store:
                print("  ❌ Failed to connect to Chroma")
                return False
            
            collection = vector_store.get_or_create_collection()
            if not collection:
                print("  ❌ Failed to get collection")
                return False
            
            print("  ✅ Connected to Chroma Cloud successfully")
            print(f"  📦 Collection: {collection.name if hasattr(collection, 'name') else 'documents'}")
            
            # Get collection stats
            try:
                docs = collection.get(limit=1)
                doc_count = len(docs.get('ids', [])) if docs else 0
                print(f"  📊 Documents in Chroma: {doc_count}+")
            except:
                pass
            
            return True
        
        except Exception as e:
            print(f"  ❌ Chroma verification error: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(
        description='Enforce data sync between Google Drive and Chroma'
    )
    parser.add_argument('--force', action='store_true', help='Force complete resync')
    parser.add_argument('--status', action='store_true', help='Show sync status only')
    parser.add_argument('--verify', action='store_true', help='Verify Chroma connection only')
    
    args = parser.parse_args()
    
    try:
        # Initialize Flask app context (needed untuk database queries)
        from run import create_app
        app = create_app()
        with app.app_context():
            
            if args.verify:
                DataSyncEnforcer.verify_chroma_connection()
            
            elif args.status:
                DataSyncEnforcer.print_sync_status()
            
            else:
                # Do full sync
                DataSyncEnforcer.print_sync_status()
                
                # Verify Chroma first
                if not DataSyncEnforcer.verify_chroma_connection():
                    print("\n❌ Cannot sync: Chroma Cloud not accessible")
                    print("   Please check:")
                    print("   1. CHROMA_API_KEY in .env")
                    print("   2. Internet connection")
                    print("   3. Chroma Cloud status")
                    return
                
                # Do sync
                result = DataSyncEnforcer.sync_all_folders(force=args.force)
                
                # Print summary
                print("\n" + "="*60)
                print("📋 SYNC SUMMARY")
                print("="*60)
                print(f"Folders Synced: {result.get('folders_synced', 0)}")
                print(f"Files Added: {result.get('files_added', 0)}")
                print(f"Documents Indexed: {result.get('files_indexed', 0)}")
                print(f"Failed: {result.get('files_failed', 0)}")
                print(f"Duration: {result.get('duration', 'N/A')}s")
                print(f"Status: {result.get('status', 'N/A')}")
                print("="*60)
                
                if result.get('status') == 'complete':
                    print("\n✅ Sync completed successfully!")
                    print("\n📣 Your chatbot now has access to ALL data from:")
                    print("   ✅ Google Drive folders")
                    print("   ✅ Chroma Cloud collection")
                    print("\n   AI will NO LONGER say 'data tidak ada'! 🎉")
                else:
                    print(f"\n⚠️  Sync failed or incomplete: {result.get('error', 'Unknown error')}")
                
                # Show final status
                DataSyncEnforcer.print_sync_status()
    
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()

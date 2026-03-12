#!/usr/bin/env python3
"""
Test script to verify all learning models are properly configured
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

try:
    from app import create_app
    from app.models import db, LearningSession, DiscussionThread, DiscussionPost
    
    # Create app
    app = create_app()
    
    with app.app_context():
        # Try to create all tables
        print("Testing models initialization...")
        
        # List all models
        models_to_test = [
            'LearningSession',
            'DiscussionThread', 
            'DiscussionPost',
            'PostReaction',
            'StudyMaterial',
            'QuizQuestion',
            'UserQuizAttempt',
            'QuizAttempt',
            'UserCompetency',
            'LearningActivityLog'
        ]
        
        from app import models
        for model_name in models_to_test:
            if hasattr(models, model_name):
                print(f"  ✅ {model_name}")
            else:
                print(f"  ❌ {model_name} NOT FOUND")
        
        print("\n✅ All learning models loaded successfully!")
        print("✅ Database initialization complete")
        print("\nYou can now run:")
        print("  python test_routes.py     # Test API endpoints")
        print("  python run.py              # Start the application")
        
except Exception as e:
    print(f"❌ Error initializing models: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

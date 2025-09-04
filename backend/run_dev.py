#!/usr/bin/env python3
"""
Development server runner dengan fallback untuk database
"""

import os
import sys
import asyncio
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

def check_database_connection():
    """Check if database is available"""
    try:
        import asyncpg
        return True
    except ImportError:
        return False

def create_mock_database():
    """Create mock database configuration"""
    os.environ["DATABASE_URL"] = "sqlite:///./test.db"
    os.environ["REDIS_URL"] = "redis://localhost:6379/0"
    os.environ["AI_ENABLED"] = "true"
    os.environ["GROQ_API_KEY"] = "test-key"

async def main():
    """Main function"""
    print("🚀 Starting Pentest Lab Development Server...")
    
    # Check if database dependencies are available
    if not check_database_connection():
        print("⚠️  Database dependencies not available, using mock configuration")
        create_mock_database()
    
    # Import and run the app
    try:
        import uvicorn
        from main import app
        
        print("✅ Starting server on http://localhost:8000")
        print("📚 API Documentation: http://localhost:8000/docs")
        print("🛡️  Pentest Lab Ready!")
        
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Try installing minimal requirements: pip install -r requirements-minimal.txt")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    asyncio.run(main())

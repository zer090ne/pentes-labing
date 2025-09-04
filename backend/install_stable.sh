#!/bin/bash

# Script untuk install dependencies yang stabil untuk Python 3.13
echo "🔧 Installing stable dependencies for Python 3.13..."

# Install satu per satu untuk menghindari error
echo "📦 Installing core framework..."
pip install fastapi==0.103.2
pip install uvicorn[standard]==0.23.2

echo "📦 Installing pydantic (older stable version)..."
pip install pydantic==2.3.0
pip install pydantic-settings==2.0.3

echo "📦 Installing database..."
pip install sqlalchemy==2.0.20
pip install alembic==1.12.1

echo "📦 Installing background tasks..."
pip install celery==5.3.1
pip install flower==2.0.1

echo "📦 Installing authentication..."
pip install python-jose[cryptography]==3.3.0
pip install passlib[bcrypt]==1.7.4
pip install python-multipart==0.0.6

echo "📦 Installing HTTP client..."
pip install httpx==0.24.1
pip install aiofiles==23.1.0

echo "📦 Installing WebSocket..."
pip install websockets==11.0.3

echo "📦 Installing utilities..."
pip install python-dotenv==1.0.0
pip install loguru==0.7.0
pip install rich==13.4.2

echo "📦 Installing development tools..."
pip install pytest==7.4.0
pip install pytest-asyncio==0.21.1
pip install black==23.7.0
pip install isort==5.12.0
pip install flake8==6.0.0

echo "📦 Installing AI integration..."
pip install groq==0.4.1
pip install openai==1.3.0

echo "✅ All dependencies installed successfully!"
echo "🚀 You can now run: python run_dev.py"

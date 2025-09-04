#!/bin/bash

# Script untuk install dependencies di Kali Linux
echo "🔧 Installing system dependencies..."

# Install PostgreSQL development headers
sudo apt-get update
sudo apt-get install -y \
    postgresql-server-dev-all \
    libpq-dev \
    python3-dev \
    build-essential \
    libssl-dev \
    libffi-dev

# Install pentest tools
echo "🛡️ Installing pentest tools..."
sudo apt-get install -y \
    nmap \
    nikto \
    hydra \
    sqlmap \
    gobuster \
    dirb \
    dirbuster \
    wapiti \
    w3af \
    skipfish

echo "✅ System dependencies installed successfully!"
echo "📦 Now you can run: pip install -r requirements.txt"

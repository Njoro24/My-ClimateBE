#!/bin/bash
# Render build script for Climate Witness Chain

echo "🚀 Starting Climate Witness Chain build for Render..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r render_requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p uploads logs temp

# Set permissions
echo "🔧 Setting permissions..."
chmod +x render_start.py

# Initialize database (will be done at runtime)
echo "✅ Build completed successfully!"
echo "🎯 Ready for deployment on Render"
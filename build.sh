#!/bin/bash
set -e

echo "🔨 Building File Merger Pro..."

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install requirements
pip install -r requirements.txt

echo "✅ Build complete!"

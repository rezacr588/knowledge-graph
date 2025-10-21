#!/bin/bash

# Restart all development services

echo "🔄 Restarting Hybrid RAG System..."
echo ""

# Stop everything first
./stop_dev.sh

# Wait a moment
echo ""
echo "⏳ Waiting 3 seconds..."
sleep 3

# Start everything
echo ""
./start_dev.sh

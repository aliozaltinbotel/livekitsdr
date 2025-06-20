#!/bin/bash

# Azure App Service startup script for Next.js

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install --production
fi

# Start the Next.js application
echo "Starting Next.js application..."
npm run start
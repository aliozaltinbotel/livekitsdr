#!/bin/bash

echo "🚀 Setting up LiveKit Voice Assistant..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your API credentials before continuing!"
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Setup Python agent
echo "🐍 Setting up Python agent..."
cd agent
if [ ! -f .env ]; then
    cp ../.env .env
fi

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

echo "✅ Agent setup complete!"

# Setup frontend
echo "⚛️  Setting up Next.js frontend..."
cd ../frontend

# Create .env.local from root .env
if [ ! -f .env.local ]; then
    echo "LIVEKIT_URL=$LIVEKIT_URL" > .env.local
    echo "LIVEKIT_API_KEY=$LIVEKIT_API_KEY" >> .env.local
    echo "LIVEKIT_API_SECRET=$LIVEKIT_API_SECRET" >> .env.local
fi

# Install dependencies
pnpm install

echo "✅ Frontend setup complete!"

echo ""
echo "🎉 Setup complete! Next steps:"
echo "1. Start the agent: cd agent && source venv/bin/activate && python agent.py start"
echo "2. Start the frontend: cd frontend && pnpm dev"
echo "3. Open http://localhost:3000 in your browser"
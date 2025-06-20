FROM python:3.11-slim

WORKDIR /app

# LiveKit agent for voice assistant - with .env support

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Copy Google service account key if it exists
COPY botelai-*.json* ./

# Run the agent
CMD ["python", "agent.py", "start"]
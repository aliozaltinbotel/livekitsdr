FROM python:3.11-slim

WORKDIR /app

# LiveKit agent for voice assistant

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Copy environment files (these should be added during build/deployment)
# The .env file will be copied if it exists
COPY .env* ./

# Copy Google service account key if it exists
COPY botelai-*.json* ./

# Set environment variable for Google service account
ENV GOOGLE_SERVICE_ACCOUNT_KEY=/app/botelai-d95567fc3ae3.json

# Run the agent
CMD ["python", "agent.py", "start"]
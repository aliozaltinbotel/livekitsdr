FROM python:3.11-slim

WORKDIR /app

# LiveKit agent with integrated MCP server

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install agent requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy and install MCP server requirements
COPY pms_mcp_server/requirements.txt /app/pms_mcp_server/
RUN pip install --no-cache-dir -r pms_mcp_server/requirements.txt

# Copy application code
COPY . .

# Copy Google service account key if it exists
COPY botelai-*.json* ./

# Make startup script executable
RUN chmod +x start_production.sh

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PMS_MCP_SERVER_URL=http://localhost:3001/sse

# Health check for MCP server
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:3001/health || exit 1

# Run both MCP server and agent
CMD ["./start_production.sh"]
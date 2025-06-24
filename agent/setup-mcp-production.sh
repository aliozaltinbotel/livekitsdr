#!/bin/bash

# Setup PMS MCP Server for production deployment
# This script sets up the MCP server as a systemd service

set -e

echo "=========================================="
echo "Setting up PMS MCP Server for Production"
echo "=========================================="

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then 
    echo "Please run with sudo: sudo $0"
    exit 1
fi

# Configuration
MCP_DIR="/opt/pms-mcp-server"
MCP_USER="mcp-server"
MCP_PORT="3001"
SERVICE_NAME="pms-mcp-server"

# Create dedicated user for MCP server
if ! id "$MCP_USER" &>/dev/null; then
    echo "Creating user $MCP_USER..."
    useradd -r -s /bin/false -d "$MCP_DIR" "$MCP_USER"
fi

# Create directory structure
echo "Creating directory structure..."
mkdir -p "$MCP_DIR"
mkdir -p "$MCP_DIR/logs"

# Copy MCP server files
echo "Copying MCP server files..."
cp -r pms_mcp_server/* "$MCP_DIR/"

# Create virtual environment and install dependencies
echo "Setting up Python environment..."
cd "$MCP_DIR"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create environment file
echo "Creating environment file..."
cat > "$MCP_DIR/.env.production" << EOF
# PMS MCP Server Production Configuration
NODE_ENV=production
PORT=$MCP_PORT

# PMS API Configuration
PMS_API_URL=${PMS_API_URL:-https://api-dev.botel.ai}
PMS_API_KEY=${PMS_API_KEY}

# Security
MCP_AUTH_TOKEN=${PMS_MCP_SERVER_TOKEN}

# Logging
LOG_LEVEL=info
LOG_FILE=/opt/pms-mcp-server/logs/mcp-server.log
EOF

# Set permissions
chown -R "$MCP_USER:$MCP_USER" "$MCP_DIR"
chmod 600 "$MCP_DIR/.env.production"

# Create systemd service
echo "Creating systemd service..."
cat > "/etc/systemd/system/$SERVICE_NAME.service" << EOF
[Unit]
Description=PMS MCP Server for LiveKit Agent
After=network.target

[Service]
Type=simple
User=$MCP_USER
WorkingDirectory=$MCP_DIR
Environment="NODE_ENV=production"
EnvironmentFile=$MCP_DIR/.env.production
ExecStart=$MCP_DIR/venv/bin/python -m src
Restart=always
RestartSec=10

# Logging
StandardOutput=append:$MCP_DIR/logs/mcp-server.log
StandardError=append:$MCP_DIR/logs/mcp-server-error.log

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$MCP_DIR/logs

[Install]
WantedBy=multi-user.target
EOF

# Create log rotation config
echo "Setting up log rotation..."
cat > "/etc/logrotate.d/$SERVICE_NAME" << EOF
$MCP_DIR/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 $MCP_USER $MCP_USER
    sharedscripts
    postrotate
        systemctl reload $SERVICE_NAME > /dev/null 2>&1 || true
    endscript
}
EOF

# Enable and start service
echo "Enabling and starting service..."
systemctl daemon-reload
systemctl enable "$SERVICE_NAME"
systemctl start "$SERVICE_NAME"

# Check service status
sleep 2
if systemctl is-active --quiet "$SERVICE_NAME"; then
    echo "✓ MCP server is running!"
else
    echo "✗ Failed to start MCP server"
    echo "Check logs: journalctl -u $SERVICE_NAME -n 50"
    exit 1
fi

# Create health check script
echo "Creating health check script..."
cat > "/usr/local/bin/check-mcp-server" << 'EOF'
#!/bin/bash
# Health check for PMS MCP Server

if curl -f -s -o /dev/null "http://localhost:3001/health"; then
    echo "MCP server is healthy"
    exit 0
else
    echo "MCP server health check failed"
    systemctl restart pms-mcp-server
    exit 1
fi
EOF
chmod +x "/usr/local/bin/check-mcp-server"

# Add cron job for health checks
echo "Setting up health check cron job..."
(crontab -l 2>/dev/null; echo "*/5 * * * * /usr/local/bin/check-mcp-server > /dev/null 2>&1") | crontab -

echo "=========================================="
echo "MCP Server Production Setup Complete!"
echo "=========================================="
echo ""
echo "Service name: $SERVICE_NAME"
echo "Status: systemctl status $SERVICE_NAME"
echo "Logs: journalctl -u $SERVICE_NAME -f"
echo "Config: $MCP_DIR/.env.production"
echo ""
echo "Next steps:"
echo "1. Update $MCP_DIR/.env.production with your API keys"
echo "2. Restart service: systemctl restart $SERVICE_NAME"
echo "3. Update agent .env with PMS_MCP_SERVER_URL=http://localhost:$MCP_PORT"
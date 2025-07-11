#!/bin/bash

# Navigate to the pms_mcp_server directory
cd /Users/aliozaltin/Desktop/livekitsdr/agent/pms_mcp_server

# Activate virtual environment
source venv/bin/activate

# Load environment variables from .env file
source .env

# Export environment variables (in case .env doesn't work)
export PMS_API_KEY="eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IndLampsSFoyV0R6aWVRcXBrMG1DdyJ9.eyJpc3MiOiJodHRwczovL2JvdGVsLnVzLmF1dGgwLmNvbS8iLCJzdWIiOiJ1b2hVakxHdW1uakZPbG42TDhvMFpsNHk2SEVoVEFZWkBjbGllbnRzIiwiYXVkIjoiaHR0cHM6Ly9wbXMuYm90ZWwuYWkiLCJpYXQiOjE3NTA3NjQxMTQsImV4cCI6MTc1MDg1MDUxNCwic2NvcGUiOiJyZWFkOm1lc3NhZ2UgcmVhZDpwcm9wZXJ0eSByZWFkOnJlc2VydmF0aW9uIHJlYWQ6dXNlcnMgY3JlYXRlOnVzZXJzIiwiZ3R5IjoiY2xpZW50LWNyZWRlbnRpYWxzIiwiYXpwIjoidW9oVWpMR3VtbmpGT2xuNkw4bzBabDR5NkhFaFRBWVoiLCJwZXJtaXNzaW9ucyI6WyJyZWFkOm1lc3NhZ2UiLCJyZWFkOnByb3BlcnR5IiwicmVhZDpyZXNlcnZhdGlvbiIsInJlYWQ6dXNlcnMiLCJjcmVhdGU6dXNlcnMiXX0.jgt2uQ0W2enl3eFy0anWdStnCPCBtCNKb-9yIR79lZIMK9bZZTikiTMgfSpqfwW2PY75ru7YR0pgyIAd_CS7V6HMNLKgRv2iqpFO_zNQR5DsT5Izk-fau5mRZ_9p3vtr2D8pLx4C5AEIMi5GGIRvxXgbbA6Bz9jmDrlh2NCslvBE0pWDdKMlyOyduv7w0hYVskzouYQ6yr3jB8KaHU_gLyWsYEGyL3aPrCjp0STDjKw0KEbzoRMzXnUfExfbN9qQoQkqgJwPyOxYEc048J9C5USz8XV68nog6mhmmktIOASnNrR9lZziO7vaF9KZKcyETshKGmZ8XFalfe9ON6CrRA"
export PMS_CUSTOMER_ID="ae0c85c5-7fa7-4e09-8a94-0df5da38e72e"
export PYTHONPATH=/Users/aliozaltin/Desktop/livekitsdr/agent/pms_mcp_server

# Run the HTTP server
echo "Starting PMS MCP HTTP Server..."
echo "Python: $(which python)"
echo "Version: $(python --version)"
echo ""

python -m src.http_server
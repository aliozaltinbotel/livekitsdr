# Cursor IDE Configuration for PMS MCP Server

## Setup Instructions

### 1. Prerequisites

- Cursor IDE installed
- Python 3.10+ (we're using Python 3.12)
- Virtual environment created and dependencies installed

### 2. MCP Configuration

To connect Cursor IDE to the local PMS MCP server, you need to add the following configuration to Cursor's MCP settings:

1. Open Cursor IDE
2. Go to **Settings** → **MCP** (or press `Cmd+,` and search for "MCP")
3. Add the following configuration:

```json
{
  "mcpServers": {
    "pms-local": {
      "command": "/Users/aliozaltin/pmsmcp/pms_mcp_server/venv/bin/python",
      "args": ["-m", "src.server"],
      "cwd": "/Users/aliozaltin/pmsmcp/pms_mcp_server",
      "env": {
        "PMS_API_KEY": "your-bearer-token-here",
        "PMS_CUSTOMER_ID": "your-customer-id-here",
        "PYTHONPATH": "/Users/aliozaltin/pmsmcp/pms_mcp_server"
      }
    }
  }
}
```

### 3. Alternative: Using Shell Script

You can also configure Cursor to use the shell script:

```json
{
  "mcpServers": {
    "pms-local": {
      "command": "/bin/bash",
      "args": ["/Users/aliozaltin/pmsmcp/pms_mcp_server/run_server.sh"],
      "cwd": "/Users/aliozaltin/pmsmcp/pms_mcp_server"
    }
  }
}
```

### 4. Testing the Connection

1. After adding the configuration, restart Cursor IDE
2. Open a new chat or AI panel
3. The PMS MCP server should be available
4. You can test by asking Cursor:
   - "Get the customer's property context"
   - "Show me all properties for this customer"
   - "What properties does this customer have?"

### 5. Available Tool

The server provides a single, focused tool:

**get_customer_properties_context**

This tool fetches all properties for the configured customer and returns detailed context information formatted for LLM consumption. It includes:

- Property names and IDs
- Active/inactive status
- Location details
- Capacity information
- Property types
- Coordinates
- Description previews

Perfect for providing property context to AI assistants in customer service, booking management, or property inquiries.

### 6. Troubleshooting

If the server doesn't connect:

1. Check that the virtual environment is properly activated
2. Verify Python version: `python --version` (should be 3.10+)
3. Check that all dependencies are installed: `pip list`
4. Try running the server manually: `./run_server.sh`
5. Check Cursor's developer console for errors

### 7. Environment Variables

The server uses these environment variables:
- `PMS_API_KEY`: Your PMS Bearer token (required)
- `PMS_CUSTOMER_ID`: Your customer ID for API requests (required)
- `PMS_BASE_URL`: API base URL (optional, defaults to https://pms.botel.ai)

For production use, replace the placeholders with your actual Bearer token and customer ID.

**Note**: The API uses Bearer token authentication and requires a customerID header on all requests.
# PMS MCP Server

A streamlined Model Context Protocol (MCP) server for Botel PMS API integration, providing property context to LLMs.

## Features

- **Single Purpose Tool**: Fetches all customer properties and their details
- **Automatic Context Building**: Provides formatted property information for LLM consumption
- **High Performance**: Optimized API calls with pagination support
- **Secure Authentication**: Bearer token with customer ID header

## Installation

```bash
pip install pms-mcp-server
```

Or install from source:

```bash
git clone https://github.com/botel-ai/pms-mcp-server.git
cd pms-mcp-server
pip install -e .
```

## Configuration

Set your API credentials as environment variables:

```bash
export PMS_API_KEY="your-bearer-token-here"
export PMS_CUSTOMER_ID="your-customer-id-here"
```

Optional configuration:

```bash
export PMS_BASE_URL=https://pms.botel.ai  # Default value
```

## Usage

### Running the Server

```bash
python -m src.server
```

### Cursor IDE Integration

Add to your Cursor IDE MCP configuration:

```json
{
  "mcpServers": {
    "pms": {
      "command": "python",
      "args": ["-m", "src.server"],
      "cwd": "/path/to/pms-mcp-server",
      "env": {
        "PMS_API_KEY": "your-bearer-token-here",
        "PMS_CUSTOMER_ID": "your-customer-id-here"
      }
    }
  }
}
```

## Available Tool

### get_customer_properties_context

Fetches all properties for the customer and provides detailed context information.

**Parameters:**
- `include_inactive` (boolean, optional): Include inactive properties. Default: false

**Returns:**
A formatted context document containing:
- Total property count
- Active/inactive property breakdown
- For each property:
  - Name and status
  - Location details
  - Capacity information
  - Property type
  - Coordinates
  - Description preview

**Example Output:**
```markdown
# Customer Property Context
Total Properties: 1
Active Properties: 1

## Property 1: Spacious Villa Perfect for Families & Friends
- **Status**: Active
- **ID**: fde09fba-3a96-4705-a0c4-4bd264fb61da
- **Location**: Mugla, TR
- **Max Occupancy**: 8 guests
- **Type**: Villa
- **Coordinates**: 36.839778, 28.14375

## Summary
This customer has 1 properties in the system.
1 properties are currently active and available for bookings.
```

## API Documentation

Full API documentation is available at: https://pms.botel.ai/swagger/v1/swagger.json

## Authentication

The server uses:
- **Bearer Token**: Added to Authorization header
- **Customer ID**: Added to customerId header on all requests

## Security

- Always use HTTPS in production
- Keep your API key secure and never commit it to version control
- Use environment variables or secure key management systems

## Support

For support, please contact: support@botel.ai

## License

This project is licensed under the MIT License.